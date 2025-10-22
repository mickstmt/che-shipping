# app/services/router_service.py
import requests
import json
import os
from typing import Dict, Optional, Tuple
import logging

class RouterService:
    """
    Servicio para interactuar con OpenRouteService API para cálculo de rutas en Chile
    """

    def __init__(self):
        self.api_key = os.environ.get('ROUTER_SERVICE_API_KEY') or "eyJvcmciOiI1YjNjZTM1OTc4NTExMTAwMDFjZjYyNDgiLCJpZCI6IjYwYTM2ZDg1MTA1YTRiM2U5MjFmZjdlM2RmZjlhMTkyIiwiaCI6Im11cm11cjY0In0="
        self.base_url = "https://api.openrouteservice.org"
        self.timeout = 30

        # Leer origen desde .env
        default_origin_address = os.environ.get('DEFAULT_ORIGIN_ADDRESS', 'Santiago Centro, Chile')
        default_origin_name = os.environ.get('DEFAULT_ORIGIN_NAME', '')

        # Intentar detectar si es una coordenada (formato: "lat,lng")
        if ',' in default_origin_address and not any(c.isalpha() for c in default_origin_address):
            try:
                parts = default_origin_address.split(',')
                if len(parts) == 2:
                    lat, lng = float(parts[0].strip()), float(parts[1].strip())
                    # Usar nombre personalizado si existe, sino usar coordenadas
                    display_name = default_origin_name or f'Coordenadas: {lat}, {lng}'
                    self.default_origin = {
                        'lat': lat,
                        'lng': lng,
                        'address': display_name,
                        'formatted_address': display_name,
                        'is_coords': True
                    }
                    logging.info(f"Usando coordenadas directas como origen: {lat}, {lng} ({display_name})")
                else:
                    raise ValueError("Formato de coordenadas inválido")
            except (ValueError, IndexError) as e:
                logging.warning(f"No se pudieron parsear coordenadas: {default_origin_address}")
                # Fallback a dirección de texto
                self.default_origin = {
                    'lat': -33.4372,  # Providencia centro aprox
                    'lng': -70.6167,
                    'address': default_origin_address,
                    'is_coords': False
                }
        else:
            # Es una dirección de texto
            self.default_origin = {
                'lat': None,
                'lng': None,
                'address': default_origin_address,
                'is_coords': False
            }

    def _geocode_default_origin(self):
        """Geocodificar la dirección de origen por defecto"""
        try:
            result = self.geocode_address(self.default_origin['address'])
            if result:
                self.default_origin['lat'] = result['lat']
                self.default_origin['lng'] = result['lng']
                logging.info(f"Origen geocodificado: {result['formatted_address']}")
        except Exception as e:
            logging.warning(f"No se pudo geocodificar origen por defecto: {str(e)}")

    def _normalize_address(self, address: str) -> str:
        """
        Normalizar dirección para mejorar geocodificación
        - Quita puntos de abreviaturas
        - Convierte variaciones comunes
        """
        import re

        # Normalizar el texto
        normalized = address.strip()

        # Reemplazar abreviaturas comunes
        replacements = {
            r'\bav\.\s*': 'avenida ',
            r'\bave\.\s*': 'avenida ',
            r'\bclle\.\s*': 'calle ',
            r'\bpje\.\s*': 'pasaje ',
            r'\bdpto\.\s*': 'departamento ',
            r'\bdepto\.\s*': 'departamento ',
            r'\bstgo\b': 'santiago',
            r'\brm\b': 'región metropolitana',
        }

        for pattern, replacement in replacements.items():
            normalized = re.sub(pattern, replacement, normalized, flags=re.IGNORECASE)

        return normalized

    def geocode_address(self, address: str) -> Optional[Dict]:
        """
        Geocodificar una dirección usando OpenRouteService

        Args:
            address (str): Dirección a geocodificar

        Returns:
            Dict: {'lat': float, 'lng': float, 'formatted_address': str} o None si falla
        """
        try:
            # Normalizar dirección para mejor búsqueda
            normalized_address = self._normalize_address(address)

            # OpenRouteService usa GET con parámetros
            url = f"{self.base_url}/geocode/search"
            headers = {
                'Authorization': self.api_key,
                'Accept': 'application/json'
            }

            params = {
                'text': normalized_address,
                'boundary.country': 'CHL',  # Chile en formato ISO 3166-1 alpha-3
                'size': 1  # Solo necesitamos el mejor resultado
            }

            response = requests.get(url, params=params, headers=headers, timeout=self.timeout)

            if response.status_code == 200:
                data = response.json()

                if data.get('features') and len(data['features']) > 0:
                    feature = data['features'][0]
                    coordinates = feature.get('geometry', {}).get('coordinates', [])
                    properties = feature.get('properties', {})

                    if len(coordinates) >= 2:
                        return {
                            'lat': coordinates[1],  # OpenRouteService devuelve [lng, lat]
                            'lng': coordinates[0],
                            'formatted_address': properties.get('label', address),
                            'place_id': properties.get('id'),
                            'types': [properties.get('layer', 'address')]
                        }

            logging.warning(f"OpenRouteService geocoding failed: {response.status_code} - {response.text}")
            return None

        except Exception as e:
            logging.error(f"Error en geocodificación OpenRouteService: {str(e)}")
            return None
    
    def calculate_route(self, origin: Dict, destination: Dict) -> Optional[Dict]:
        """
        Calcular ruta entre dos puntos usando OpenRouteService

        Args:
            origin (Dict): {'lat': float, 'lng': float}
            destination (Dict): {'lat': float, 'lng': float}

        Returns:
            Dict: Información de la ruta o None si falla
        """
        try:
            url = f"{self.base_url}/v2/directions/driving-car"
            headers = {
                'Authorization': self.api_key,
                'Content-Type': 'application/json',
                'Accept': 'application/json'
            }

            # OpenRouteService espera coordenadas en formato [lng, lat]
            payload = {
                'coordinates': [
                    [origin['lng'], origin['lat']],
                    [destination['lng'], destination['lat']]
                ]
            }

            response = requests.post(url, json=payload, headers=headers, timeout=self.timeout)

            if response.status_code == 200:
                data = response.json()

                if data.get('routes') and len(data['routes']) > 0:
                    route = data['routes'][0]
                    summary = route.get('summary', {})

                    # Extraer información relevante
                    distance_m = summary.get('distance', 0)
                    duration_s = summary.get('duration', 0)

                    return {
                        'distance_km': round(distance_m / 1000, 2),
                        'distance_m': distance_m,
                        'duration_minutes': round(duration_s / 60),
                        'duration_seconds': duration_s,
                        'polyline': route.get('geometry'),
                        'start_address': f"{origin['lat']},{origin['lng']}",
                        'end_address': f"{destination['lat']},{destination['lng']}",
                        'status': 'OK',
                        'full_response': data
                    }

            logging.warning(f"OpenRouteService directions failed: {response.status_code} - {response.text}")
            return None

        except Exception as e:
            logging.error(f"Error en cálculo de ruta OpenRouteService: {str(e)}")
            return None
    
    def get_distance_and_time(self, origin_address: str, destination_address: str) -> Dict:
        """
        Método principal: obtener distancia y tiempo entre dos direcciones

        Args:
            origin_address (str): Dirección de origen
            destination_address (str): Dirección de destino

        Returns:
            Dict: Resultado completo con distancia, tiempo y coordenadas
        """
        try:
            # 1. Geocodificar origen (o usar coordenadas por defecto)
            if origin_address and origin_address.lower() not in ['santiago', 'santiago centro']:
                origin_geo = self.geocode_address(origin_address)
                if not origin_geo:
                    # Si falla geocodificación, usar default_origin
                    if self.default_origin.get('lat') is None:
                        # Default origin no tiene coordenadas, intentar geocodificarlo
                        logging.info(f"Geocodificando origen por defecto: {self.default_origin['address']}")
                        origin_geo = self.geocode_address(self.default_origin['address'])
                        if not origin_geo:
                            return {
                                'success': False,
                                'error': 'No se pudo geocodificar la dirección de origen',
                                'status': 'ORIGIN_GEOCODING_FAILED'
                            }
                    else:
                        origin_geo = self.default_origin
            else:
                # Usar default origin
                if self.default_origin.get('lat') is None:
                    # Default origin no tiene coordenadas, intentar geocodificarlo
                    logging.info(f"Geocodificando origen por defecto: {self.default_origin['address']}")
                    origin_geo = self.geocode_address(self.default_origin['address'])
                    if not origin_geo:
                        return {
                            'success': False,
                            'error': 'No se pudo geocodificar la dirección de origen por defecto',
                            'status': 'ORIGIN_GEOCODING_FAILED'
                        }
                else:
                    origin_geo = self.default_origin
            
            # 2. Geocodificar destino
            destination_geo = self.geocode_address(destination_address)
            if not destination_geo:
                return {
                    'success': False,
                    'error': 'No se pudo encontrar la dirección de destino',
                    'status': 'GEOCODING_FAILED'
                }
            
            # 3. Calcular ruta
            route = self.calculate_route(origin_geo, destination_geo)
            if not route:
                return {
                    'success': False,
                    'error': 'No se pudo calcular la ruta',
                    'status': 'ROUTING_FAILED'
                }
            
            # 4. Retornar resultado completo
            return {
                'success': True,
                'origin': {
                    'address': origin_address or origin_geo['address'],
                    'formatted_address': origin_geo.get('formatted_address'),
                    'lat': origin_geo['lat'],
                    'lng': origin_geo['lng']
                },
                'destination': {
                    'address': destination_address,
                    'formatted_address': destination_geo.get('formatted_address'),
                    'lat': destination_geo['lat'],
                    'lng': destination_geo['lng']
                },
                'route': {
                    'distance_km': route['distance_km'],
                    'duration_minutes': route['duration_minutes'],
                    'polyline': route.get('polyline')
                },
                'status': 'OK',
                'router_response': route['full_response']
            }
            
        except Exception as e:
            logging.error(f"Error general en RouterService: {str(e)}")
            return {
                'success': False,
                'error': f'Error interno: {str(e)}',
                'status': 'ERROR'
            }

# Instancia global del servicio
router_service = RouterService()
