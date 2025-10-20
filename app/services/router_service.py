# app/services/router_service.py
import requests
import json
import os
from typing import Dict, Optional, Tuple
import logging

class RouterService:
    """
    Servicio para interactuar con RouterService API para cálculo de rutas en Chile
    """
    
    def __init__(self):
        self.api_key = "eyJvcmciOiI1YjNjZTM1OTc4NTExMTAwMDFjZjYyNDgiLCJpZCI6IjYwYTM2ZDg1MTA1YTRiM2U5MjFmZjdlM2RmZjlhMTkyIiwiaCI6Im11cm11cjY0In0="
        self.base_url = "https://api.routerservice.com"
        self.timeout = 30
        
        # Santiago Centro como origen por defecto
        self.default_origin = {
            'lat': -33.4489,
            'lng': -70.6693,
            'address': 'Santiago Centro, Chile'
        }
    
    def geocode_address(self, address: str) -> Optional[Dict]:
        """
        Geocodificar una dirección usando RouterService
        
        Args:
            address (str): Dirección a geocodificar
            
        Returns:
            Dict: {'lat': float, 'lng': float, 'formatted_address': str} o None si falla
        """
        try:
            url = f"{self.base_url}/geocoding"
            headers = {
                'Authorization': f'Bearer {self.api_key}',
                'Content-Type': 'application/json'
            }
            
            payload = {
                'address': address,
                'country': 'CL'  # Restringir a Chile
            }
            
            response = requests.post(url, json=payload, headers=headers, timeout=self.timeout)
            
            if response.status_code == 200:
                data = response.json()
                
                if data.get('status') == 'OK' and data.get('results'):
                    result = data['results'][0]
                    location = result.get('geometry', {}).get('location', {})
                    
                    return {
                        'lat': location.get('lat'),
                        'lng': location.get('lng'),
                        'formatted_address': result.get('formatted_address', address),
                        'place_id': result.get('place_id'),
                        'types': result.get('types', [])
                    }
            
            logging.warning(f"RouterService geocoding failed: {response.status_code} - {response.text}")
            return None
            
        except Exception as e:
            logging.error(f"Error en geocodificación RouterService: {str(e)}")
            return None
    
    def calculate_route(self, origin: Dict, destination: Dict) -> Optional[Dict]:
        """
        Calcular ruta entre dos puntos usando RouterService
        
        Args:
            origin (Dict): {'lat': float, 'lng': float}
            destination (Dict): {'lat': float, 'lng': float}
            
        Returns:
            Dict: Información de la ruta o None si falla
        """
        try:
            url = f"{self.base_url}/directions"
            headers = {
                'Authorization': f'Bearer {self.api_key}',
                'Content-Type': 'application/json'
            }
            
            payload = {
                'origin': f"{origin['lat']},{origin['lng']}",
                'destination': f"{destination['lat']},{destination['lng']}",
                'mode': 'driving',
                'optimize': True,
                'alternatives': False
            }
            
            response = requests.post(url, json=payload, headers=headers, timeout=self.timeout)
            
            if response.status_code == 200:
                data = response.json()
                
                if data.get('status') == 'OK' and data.get('routes'):
                    route = data['routes'][0]
                    leg = route['legs'][0]
                    
                    # Extraer información relevante
                    distance_m = leg['distance']['value']
                    duration_s = leg['duration']['value']
                    
                    return {
                        'distance_km': round(distance_m / 1000, 2),
                        'distance_m': distance_m,
                        'duration_minutes': round(duration_s / 60),
                        'duration_seconds': duration_s,
                        'polyline': route.get('overview_polyline', {}).get('points'),
                        'start_address': leg.get('start_address'),
                        'end_address': leg.get('end_address'),
                        'status': 'OK',
                        'full_response': data
                    }
            
            logging.warning(f"RouterService directions failed: {response.status_code} - {response.text}")
            return None
            
        except Exception as e:
            logging.error(f"Error en cálculo de ruta RouterService: {str(e)}")
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
                    origin_geo = self.default_origin
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
