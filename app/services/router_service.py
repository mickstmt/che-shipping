# app/services/router_service.py
"""
Servicio para cálculo de rutas y validación de direcciones usando Google Maps APIs
- Address Validation API: Para validar y geocodificar direcciones con niveles de confianza
- Distance Matrix API: Para calcular distancias y tiempos de viaje reales
"""

import googlemaps
import os
import logging
import json
import time
from typing import Dict, Optional, Tuple
from datetime import datetime, timedelta

class AddressCache:
    """Sistema de caché simple en memoria para direcciones validadas"""

    def __init__(self, max_age_hours=24):
        self.cache = {}  # {address: {data: {...}, timestamp: datetime}}
        self.max_age = timedelta(hours=max_age_hours)

    def get(self, address: str) -> Optional[Dict]:
        """Obtener dirección del caché si existe y no está expirada"""
        if address in self.cache:
            entry = self.cache[address]
            age = datetime.now() - entry['timestamp']

            if age < self.max_age:
                logging.info(f"Cache HIT para: {address}")
                return entry['data']
            else:
                # Expirado, eliminarlo
                del self.cache[address]
                logging.info(f"Cache EXPIRED para: {address}")

        return None

    def set(self, address: str, data: Dict):
        """Guardar dirección en el caché"""
        self.cache[address] = {
            'data': data,
            'timestamp': datetime.now()
        }
        logging.info(f"Cache SET para: {address}")

    def clear(self):
        """Limpiar todo el caché"""
        self.cache = {}
        logging.info("Cache cleared")


class RouterService:
    """
    Servicio para interactuar con Google Maps APIs para cálculo de rutas en Chile
    """

    # Niveles de granularidad aceptables según estrategia híbrida
    ACCEPTABLE_GRANULARITIES = [
        'PREMISE',              # Dirección exacta (edificio específico)
        'PREMISE_PROXIMITY',    # Cerca del edificio
    ]

    WARNING_GRANULARITIES = [
        'BLOCK',                # Cuadra/bloque
        'ROUTE',                # Calle/ruta sin número exacto
    ]

    REJECT_GRANULARITIES = [
        'NEIGHBORHOOD',         # Barrio
        'LOCALITY',             # Ciudad/localidad
        'SUBLOCALITY',          # Sub-localidad
        'ADMINISTRATIVE_AREA',  # Región/estado
        'OTHER',                # Otro/desconocido
    ]

    def __init__(self):
        self.api_key = os.environ.get('GOOGLE_MAPS_API_KEY')

        if not self.api_key:
            logging.error("GOOGLE_MAPS_API_KEY no configurada en variables de entorno")
            raise ValueError("GOOGLE_MAPS_API_KEY es requerida")

        # Inicializar cliente de Google Maps
        self.client = googlemaps.Client(key=self.api_key)

        # Inicializar caché
        self.address_cache = AddressCache(max_age_hours=24)

        # Leer origen desde .env
        default_origin_address = os.environ.get('DEFAULT_ORIGIN_ADDRESS', '-33.4372,-70.6167')
        default_origin_name = os.environ.get('DEFAULT_ORIGIN_NAME', 'Origen por defecto')

        # Parsear coordenadas de origen (formato: "lat,lng")
        try:
            parts = default_origin_address.split(',')
            if len(parts) == 2:
                lat, lng = float(parts[0].strip()), float(parts[1].strip())
                self.default_origin = {
                    'lat': lat,
                    'lng': lng,
                    'address': default_origin_name,
                    'formatted_address': default_origin_name,
                    'is_coords': True
                }
                logging.info(f"Origen configurado: {lat}, {lng} ({default_origin_name})")
            else:
                raise ValueError("Formato de coordenadas inválido")
        except (ValueError, IndexError) as e:
            logging.error(f"Error parseando DEFAULT_ORIGIN_ADDRESS: {e}")
            # Fallback a Providencia centro
            self.default_origin = {
                'lat': -33.4372,
                'lng': -70.6167,
                'address': 'Providencia, Santiago, Chile',
                'formatted_address': 'Providencia, Santiago, Chile',
                'is_coords': True
            }

    def validate_and_geocode_address(self, address: str) -> Dict:
        """
        Validar y geocodificar dirección usando Address Validation API

        Args:
            address (str): Dirección a validar

        Returns:
            Dict: {
                'success': bool,
                'lat': float,
                'lng': float,
                'formatted_address': str,
                'granularity': str,
                'validation_level': str,  # 'accept', 'warning', 'reject'
                'confidence': float,      # Score de confianza (0-1)
                'warning_message': str,   # Mensaje si tiene warning
                'error': str              # Mensaje de error si falla
            }
        """
        try:
            # Verificar caché primero
            cached = self.address_cache.get(address)
            if cached:
                return cached

            # Llamar a Address Validation API
            # Nota: googlemaps library no tiene método directo para Address Validation API v1
            # Usaremos el método de geocoding con components para Chile y luego validaremos

            logging.info(f"Validando dirección con Google Maps: {address}")

            # Geocoding con restricción a Chile
            result = self.client.geocode(
                address=address,
                components={'country': 'CL'},  # Restringir a Chile
                language='es'
            )

            if not result or len(result) == 0:
                return {
                    'success': False,
                    'error': 'No se pudo encontrar la dirección',
                    'validation_level': 'reject'
                }

            # Tomar el primer resultado (mejor match)
            location_data = result[0]
            geometry = location_data.get('geometry', {})
            location = geometry.get('location', {})

            lat = location.get('lat')
            lng = location.get('lng')
            formatted_address = location_data.get('formatted_address', address)

            if not lat or not lng:
                return {
                    'success': False,
                    'error': 'No se pudieron obtener coordenadas',
                    'validation_level': 'reject'
                }

            # Determinar granularidad basándose en tipos de resultado
            types = location_data.get('types', [])
            granularity = self._determine_granularity(types)

            # Determinar nivel de validación
            if granularity in self.ACCEPTABLE_GRANULARITIES:
                validation_level = 'accept'
                warning_message = None
            elif granularity in self.WARNING_GRANULARITIES:
                validation_level = 'warning'
                warning_message = (
                    f"La dirección no es muy precisa (nivel: {granularity}). "
                    "Considera agregar número de casa o especificar mejor la ubicación."
                )
            else:
                validation_level = 'reject'
                warning_message = (
                    f"La dirección es demasiado imprecisa (nivel: {granularity}). "
                    "Por favor proporciona una dirección más específica con número de casa."
                )

            # Calcular score de confianza basado en location_type
            location_type = geometry.get('location_type', 'APPROXIMATE')
            confidence = self._calculate_confidence(location_type, granularity)

            result_data = {
                'success': True,
                'lat': lat,
                'lng': lng,
                'formatted_address': formatted_address,
                'granularity': granularity,
                'validation_level': validation_level,
                'confidence': confidence,
                'warning_message': warning_message,
                'location_type': location_type,
                'types': types,
                'place_id': location_data.get('place_id')
            }

            # Guardar en caché
            self.address_cache.set(address, result_data)

            return result_data

        except googlemaps.exceptions.ApiError as e:
            logging.error(f"Google Maps API error: {str(e)}")
            return {
                'success': False,
                'error': f'Error de API: {str(e)}',
                'validation_level': 'reject'
            }
        except Exception as e:
            logging.error(f"Error validando dirección: {str(e)}")
            return {
                'success': False,
                'error': f'Error interno: {str(e)}',
                'validation_level': 'reject'
            }

    def _determine_granularity(self, types: list) -> str:
        """
        Determinar granularidad basándose en los tipos de Google Maps

        Orden de prioridad (más específico a menos específico):
        - street_address, premise -> PREMISE
        - subpremise -> PREMISE
        - route + street_number -> PREMISE
        - route (sin street_number) -> ROUTE
        - intersection -> BLOCK
        - neighborhood -> NEIGHBORHOOD
        - locality, political -> LOCALITY
        """
        if 'street_address' in types or 'premise' in types:
            return 'PREMISE'

        if 'subpremise' in types:
            return 'PREMISE'

        if 'route' in types:
            # Si tiene route, verificar si también tiene street_number
            if 'street_number' in types:
                return 'PREMISE'
            else:
                return 'ROUTE'

        if 'intersection' in types:
            return 'BLOCK'

        if 'neighborhood' in types:
            return 'NEIGHBORHOOD'

        if 'locality' in types or 'political' in types:
            return 'LOCALITY'

        if 'sublocality' in types:
            return 'SUBLOCALITY'

        if 'administrative_area_level_1' in types or 'administrative_area_level_2' in types:
            return 'ADMINISTRATIVE_AREA'

        return 'OTHER'

    def _calculate_confidence(self, location_type: str, granularity: str) -> float:
        """
        Calcular score de confianza basado en location_type y granularity

        location_type puede ser:
        - ROOFTOP: Precisión exacta
        - RANGE_INTERPOLATED: Interpolado entre dos puntos
        - GEOMETRIC_CENTER: Centro geométrico
        - APPROXIMATE: Aproximado
        """
        base_score = {
            'ROOFTOP': 1.0,
            'RANGE_INTERPOLATED': 0.8,
            'GEOMETRIC_CENTER': 0.6,
            'APPROXIMATE': 0.4
        }.get(location_type, 0.3)

        granularity_multiplier = {
            'PREMISE': 1.0,
            'PREMISE_PROXIMITY': 0.95,
            'BLOCK': 0.7,
            'ROUTE': 0.6,
            'NEIGHBORHOOD': 0.4,
            'LOCALITY': 0.3,
            'SUBLOCALITY': 0.35,
            'ADMINISTRATIVE_AREA': 0.2,
            'OTHER': 0.1
        }.get(granularity, 0.1)

        return round(base_score * granularity_multiplier, 2)

    def calculate_route(self, origin: Dict, destination: Dict) -> Optional[Dict]:
        """
        Calcular distancia y tiempo usando Distance Matrix API

        Args:
            origin (Dict): {'lat': float, 'lng': float}
            destination (Dict): {'lat': float, 'lng': float}

        Returns:
            Dict: Información de distancia y tiempo o None si falla
        """
        try:
            origin_coords = f"{origin['lat']},{origin['lng']}"
            destination_coords = f"{destination['lat']},{destination['lng']}"

            logging.info(f"Calculando ruta de {origin_coords} a {destination_coords}")

            # Llamar a Distance Matrix API
            result = self.client.distance_matrix(
                origins=[origin_coords],
                destinations=[destination_coords],
                mode='driving',
                language='es',
                units='metric'
            )

            if result['status'] != 'OK':
                logging.error(f"Distance Matrix error: {result['status']}")
                return None

            # Extraer información del primer resultado
            rows = result.get('rows', [])
            if not rows or len(rows) == 0:
                logging.error("No se encontraron rutas")
                return None

            elements = rows[0].get('elements', [])
            if not elements or len(elements) == 0:
                logging.error("No se encontraron elementos en la ruta")
                return None

            element = elements[0]

            if element['status'] != 'OK':
                logging.error(f"Elemento de ruta con error: {element['status']}")
                return None

            distance = element.get('distance', {})
            duration = element.get('duration', {})

            distance_m = distance.get('value', 0)  # Metros
            duration_s = duration.get('value', 0)  # Segundos

            return {
                'distance_km': round(distance_m / 1000, 2),
                'distance_m': distance_m,
                'distance_text': distance.get('text', f"{distance_m/1000:.2f} km"),
                'duration_minutes': round(duration_s / 60),
                'duration_seconds': duration_s,
                'duration_text': duration.get('text', f"{duration_s//60} min"),
                'start_address': origin_coords,
                'end_address': destination_coords,
                'status': 'OK'
            }

        except googlemaps.exceptions.ApiError as e:
            logging.error(f"Distance Matrix API error: {str(e)}")
            return None
        except Exception as e:
            logging.error(f"Error calculando ruta: {str(e)}")
            return None

    def get_distance_and_time(self, origin_address: str, destination_address: str) -> Dict:
        """
        Método principal: obtener distancia y tiempo entre dos direcciones

        Flujo:
        1. Usar coordenadas fijas para origen (no requiere API)
        2. Validar y geocodificar destino con Address Validation
        3. Calcular ruta con Distance Matrix API

        Args:
            origin_address (str): Dirección de origen (vacío usa default)
            destination_address (str): Dirección de destino

        Returns:
            Dict: Resultado completo con distancia, tiempo, coordenadas y validación
        """
        try:
            # 1. ORIGEN: Usar coordenadas fijas (sin API call)
            if origin_address and origin_address.strip():
                # Si el usuario especifica origen, validarlo también
                origin_validation = self.validate_and_geocode_address(origin_address)

                if not origin_validation['success']:
                    return {
                        'success': False,
                        'error': f"Error en origen: {origin_validation.get('error')}",
                        'status': 'ORIGIN_VALIDATION_FAILED'
                    }

                origin_geo = {
                    'lat': origin_validation['lat'],
                    'lng': origin_validation['lng'],
                    'formatted_address': origin_validation['formatted_address']
                }
            else:
                # Usar origen por defecto (coordenadas fijas, sin API call)
                origin_geo = self.default_origin

            # 2. DESTINO: Validar y geocodificar
            dest_validation = self.validate_and_geocode_address(destination_address)

            if not dest_validation['success']:
                return {
                    'success': False,
                    'error': dest_validation.get('error', 'Error validando destino'),
                    'status': 'DESTINATION_VALIDATION_FAILED'
                }

            # Verificar nivel de validación (rechazar si es muy impreciso)
            if dest_validation['validation_level'] == 'reject':
                return {
                    'success': False,
                    'error': dest_validation.get('warning_message', 'Dirección demasiado imprecisa'),
                    'status': 'DESTINATION_TOO_IMPRECISE',
                    'destination_validation': dest_validation
                }

            destination_geo = {
                'lat': dest_validation['lat'],
                'lng': dest_validation['lng'],
                'formatted_address': dest_validation['formatted_address']
            }

            # 3. RUTA: Calcular distancia
            route = self.calculate_route(origin_geo, destination_geo)

            if not route:
                return {
                    'success': False,
                    'error': 'No se pudo calcular la ruta',
                    'status': 'ROUTING_FAILED'
                }

            # 4. Resultado completo
            result = {
                'success': True,
                'origin': {
                    'address': origin_address or origin_geo['formatted_address'],
                    'formatted_address': origin_geo['formatted_address'],
                    'lat': origin_geo['lat'],
                    'lng': origin_geo['lng']
                },
                'destination': {
                    'address': destination_address,
                    'formatted_address': destination_geo['formatted_address'],
                    'lat': destination_geo['lat'],
                    'lng': destination_geo['lng'],
                    'validation': {
                        'level': dest_validation['validation_level'],
                        'granularity': dest_validation['granularity'],
                        'confidence': dest_validation['confidence'],
                        'warning': dest_validation.get('warning_message')
                    }
                },
                'route': {
                    'distance_km': route['distance_km'],
                    'distance_text': route['distance_text'],
                    'duration_minutes': route['duration_minutes'],
                    'duration_text': route['duration_text']
                },
                'status': 'OK'
            }

            # Agregar warning si existe
            if dest_validation['validation_level'] == 'warning':
                result['warning'] = dest_validation.get('warning_message')

            return result

        except Exception as e:
            logging.error(f"Error general en RouterService: {str(e)}")
            return {
                'success': False,
                'error': f'Error interno: {str(e)}',
                'status': 'ERROR'
            }

    def clear_cache(self):
        """Limpiar el caché de direcciones"""
        self.address_cache.clear()

    def get_cache_stats(self) -> Dict:
        """Obtener estadísticas del caché"""
        return {
            'total_entries': len(self.address_cache.cache),
            'entries': [
                {
                    'address': addr,
                    'age_minutes': int((datetime.now() - entry['timestamp']).total_seconds() / 60)
                }
                for addr, entry in self.address_cache.cache.items()
            ]
        }


# Instancia global del servicio
router_service = RouterService()
