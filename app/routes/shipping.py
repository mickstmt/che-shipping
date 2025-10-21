# app/routes/shipping.py
from flask import Blueprint, request, jsonify, render_template
from app import db
from app.models import ShippingZone, ShippingMethod, ShippingQuote
from app.services.router_service import router_service
from datetime import datetime, time
import json
import logging
from functools import wraps

bp = Blueprint('shipping', __name__, url_prefix='/shipping')

# Decorador simple para admin (sin autenticación por ahora)
def admin_required(f):
    """Decorador simple - por ahora sin autenticación"""
    @wraps(f)
    def decorated_function(*args, **kwargs):
        # Por ahora permitir todo - puedes agregar autenticación después
        return f(*args, **kwargs)
    return decorated_function

def find_zone_for_distance(distance_km):
    """Encontrar zona de envío para una distancia específica"""
    zone = ShippingZone.query.filter(
        ShippingZone.min_km <= distance_km,
        ShippingZone.max_km >= distance_km,
        ShippingZone.is_active == True
    ).first()
    
    return zone

# ========================================
# API ENDPOINTS PARA JUMPSELLER
# ========================================

@bp.route('/api/quote', methods=['POST'])
def get_shipping_quote():
    """
    Endpoint principal para cotizar envío desde Jumpseller
    
    POST /shipping/api/quote
    {
        "origin": "Santiago Centro, Chile" (opcional),
        "destination": "Dirección de destino",
        "session_id": "optional_session_id"
    }
    """
    try:
        data = request.get_json()
        
        if not data:
            return jsonify({
                'success': False,
                'error': 'No se enviaron datos JSON'
            }), 400
        
        destination = data.get('destination')
        origin = data.get('origin', 'Santiago Centro, Chile')
        session_id = data.get('session_id')
        
        if not destination:
            return jsonify({
                'success': False,
                'error': 'La dirección de destino es requerida'
            }), 400
        
        # Calcular distancia usando RouterService
        route_result = router_service.get_distance_and_time(origin, destination)
        
        if not route_result['success']:
            return jsonify({
                'success': False,
                'error': f"Error al calcular ruta: {route_result.get('error', 'Unknown')}",
                'router_status': route_result.get('status')
            }), 400
        
        distance_km = route_result['route']['distance_km']
        duration_minutes = route_result['route']['duration_minutes']
        
        # Obtener métodos de envío disponibles
        available_methods = ShippingMethod.query.filter_by(is_active=True).all()
        shipping_options = []
        
        for method in available_methods:
            # Verificar si está dentro del horario
            if not method.is_available_now():
                continue
            
            # Verificar si está dentro del rango de distancia
            if distance_km > method.max_km:
                continue
            
            # Encontrar zona de precio
            zone = find_zone_for_distance(distance_km)
            
            if not zone:
                continue
            
            # Crear cotización en la base de datos
            quote = ShippingQuote(
                session_id=session_id,
                origin_address=route_result['origin']['formatted_address'],
                destination_address=route_result['destination']['formatted_address'],
                origin_lat=route_result['origin']['lat'],
                origin_lng=route_result['origin']['lng'],
                destination_lat=route_result['destination']['lat'],
                destination_lng=route_result['destination']['lng'],
                distance_km=distance_km,
                duration_minutes=duration_minutes,
                shipping_method_id=method.id,
                zone_id=zone.id,
                price_clp=zone.price_clp,
                is_available=True,
                router_response=json.dumps(route_result['router_response'])
            )
            
            db.session.add(quote)
            
            shipping_options.append({
                'method_code': method.code,
                'method_name': method.name,
                'description': method.description,
                'price_clp': zone.price_clp,
                'price_formatted': f'${zone.price_clp:,}',
                'distance_km': distance_km,
                'duration_minutes': duration_minutes,
                'duration_text': f'{duration_minutes} minutos',
                'available_until': method.end_time.strftime('%H:%M'),
                'zone_range': f'{zone.min_km}-{zone.max_km} km',
                'quote_id': quote.id
            })
        
        db.session.commit()
        
        if not shipping_options:
            return jsonify({
                'success': False,
                'error': f'No hay métodos de envío disponibles para {distance_km} km',
                'distance_km': distance_km,
                'max_distance': 7.0,
                'available_zones': [
                    f'{z.min_km}-{z.max_km}km' 
                    for z in ShippingZone.query.filter_by(is_active=True).all()
                ]
            }), 400
        
        return jsonify({
            'success': True,
            'origin': route_result['origin'],
            'destination': route_result['destination'],
            'route': route_result['route'],
            'shipping_options': shipping_options,
            'session_id': session_id,
            'quote_count': len(shipping_options)
        })
        
    except Exception as e:
        db.session.rollback()
        logging.error(f"Error en cotización de envío: {str(e)}")
        return jsonify({
            'success': False,
            'error': f'Error interno del servidor: {str(e)}'
        }), 500

@bp.route('/api/test-address', methods=['POST'])
def test_address():
    """
    Endpoint para probar geocodificación de direcciones
    """
    try:
        data = request.get_json()
        address = data.get('address')
        
        if not address:
            return jsonify({
                'success': False,
                'error': 'La dirección es requerida'
            }), 400
        
        # Probar geocodificación
        geo_result = router_service.geocode_address(address)
        
        if geo_result:
            return jsonify({
                'success': True,
                'address': address,
                'geocoded': geo_result
            })
        else:
            return jsonify({
                'success': False,
                'error': 'No se pudo geocodificar la dirección',
                'address': address
            }), 400
            
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@bp.route('/api/methods', methods=['GET'])
def get_shipping_methods():
    """Obtener métodos de envío disponibles"""
    try:
        methods = ShippingMethod.query.filter_by(is_active=True).all()
        
        return jsonify({
            'success': True,
            'methods': [method.to_dict() for method in methods],
            'count': len(methods)
        })
        
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@bp.route('/api/zones', methods=['GET'])
def get_shipping_zones():
    """Obtener zonas de envío y tarifas"""
    try:
        zones = ShippingZone.query.filter_by(is_active=True).order_by(ShippingZone.min_km).all()
        
        return jsonify({
            'success': True,
            'zones': [zone.to_dict() for zone in zones],
            'count': len(zones)
        })
        
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

# ========================================
# PANEL DE ADMINISTRACIÓN
# ========================================

@bp.route('/')
def index():
    """Panel principal de gestión de envíos"""
    return render_template('shipping/index.html', title='Gestión de Envíos')

@bp.route('/admin/methods')
@admin_required
def manage_methods():
    """Gestión de métodos de envío"""
    methods = ShippingMethod.query.all()
    return render_template('shipping/methods.html', methods=methods, title='Métodos de Envío')

@bp.route('/admin/zones')
@admin_required
def manage_zones():
    """Gestión de zonas de envío"""
    zones = ShippingZone.query.order_by(ShippingZone.min_km).all()
    return render_template('shipping/zones.html', zones=zones, title='Zonas de Envío')

@bp.route('/admin/quotes')
def view_quotes():
    """Ver cotizaciones realizadas"""
    page = request.args.get('page', 1, type=int)
    quotes = ShippingQuote.query.order_by(ShippingQuote.created_at.desc()).limit(50).all()
    return render_template('shipping/quotes.html', quotes=quotes, title='Cotizaciones')

# ========================================
# API CRUD PARA ADMIN (simplificado)
# ========================================

@bp.route('/admin/api/methods', methods=['GET'])
@admin_required
def api_get_methods():
    """API: Obtener métodos de envío"""
    methods = ShippingMethod.query.all()
    return jsonify({
        'success': True,
        'methods': [method.to_dict() for method in methods]
    })

@bp.route('/admin/api/zones', methods=['GET'])
@admin_required
def api_get_zones():
    """API: Obtener zonas de envío"""
    zones = ShippingZone.query.order_by(ShippingZone.min_km).all()
    return jsonify({
        'success': True,
        'zones': [zone.to_dict() for zone in zones]
    })

@bp.route('/admin/api/quotes/stats', methods=['GET'])
def api_quotes_stats():
    """API: Estadísticas de cotizaciones"""
    try:
        from datetime import date, timedelta
        
        today = date.today()
        
        # Cotizaciones de hoy
        today_quotes = ShippingQuote.query.filter(
            db.func.date(ShippingQuote.created_at) == today
        ).count()
        
        # Total de cotizaciones
        total_quotes = ShippingQuote.query.count()
        
        return jsonify({
            'success': True,
            'stats': {
                'today_quotes': today_quotes,
                'total_quotes': total_quotes
            }
        })
        
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

# ========================================
# INICIALIZACIÓN DE DATOS POR DEFECTO
# ========================================

@bp.route('/admin/api/init-default-data', methods=['POST'])
@admin_required
def init_default_data():
    """API: Inicializar datos por defecto del sistema"""
    try:
        # Verificar si ya hay datos
        if ShippingMethod.query.count() > 0 or ShippingZone.query.count() > 0:
            return jsonify({
                'success': False,
                'error': 'Ya existen datos en el sistema. Usa reset para reinicializar.'
            }), 400
        
        # Crear métodos de envío por defecto
        methods = [
            {
                'name': 'Envío Hoy',
                'code': 'envio_hoy',
                'description': 'Entrega el mismo día (disponible hasta las 18:00)',
                'start_time': time(0, 1),   # 00:01
                'end_time': time(18, 0),    # 18:00
                'max_km': 7.0
            },
            {
                'name': 'Envío Programado',
                'code': 'envio_programado',
                'description': 'Entrega programada para el día siguiente',
                'start_time': time(0, 0),   # 00:00
                'end_time': time(23, 59),   # 23:59
                'max_km': 7.0
            }
        ]
        
        for method_data in methods:
            method = ShippingMethod(**method_data)
            db.session.add(method)
        
        # Crear zonas de envío por defecto
        zones = [
            {'min_km': 0.0, 'max_km': 3.0, 'price_clp': 3500},
            {'min_km': 3.0, 'max_km': 4.0, 'price_clp': 4500},
            {'min_km': 4.0, 'max_km': 5.0, 'price_clp': 5000},
            {'min_km': 5.0, 'max_km': 6.0, 'price_clp': 5500},
            {'min_km': 6.0, 'max_km': 7.0, 'price_clp': 6500}
        ]
        
        for zone_data in zones:
            zone = ShippingZone(**zone_data)
            db.session.add(zone)
        
        db.session.commit()
        
        return jsonify({
            'success': True,
            'message': 'Datos por defecto inicializados correctamente',
            'methods_created': len(methods),
            'zones_created': len(zones)
        })
        
    except Exception as e:
        db.session.rollback()
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

# ========================================
# CRUD COMPLETO PARA MÉTODOS DE ENVÍO
# ========================================

@bp.route('/admin/api/methods', methods=['POST'])
@admin_required
def create_method():
    """API: Crear nuevo método de envío"""
    try:
        data = request.get_json()

        # Validar campos requeridos
        required_fields = ['name', 'code', 'start_time', 'end_time', 'max_km']
        for field in required_fields:
            if field not in data:
                return jsonify({
                    'success': False,
                    'error': f'Campo requerido: {field}'
                }), 400

        # Verificar que el código no exista
        existing = ShippingMethod.query.filter_by(code=data['code']).first()
        if existing:
            return jsonify({
                'success': False,
                'error': f'Ya existe un método con el código "{data["code"]}"'
            }), 400

        # Parsear horas
        from datetime import datetime as dt
        start_time = dt.strptime(data['start_time'], '%H:%M').time()
        end_time = dt.strptime(data['end_time'], '%H:%M').time()

        # Crear método
        method = ShippingMethod(
            name=data['name'],
            code=data['code'],
            description=data.get('description', ''),
            start_time=start_time,
            end_time=end_time,
            max_km=float(data['max_km']),
            is_active=data.get('is_active', True)
        )

        db.session.add(method)
        db.session.commit()

        return jsonify({
            'success': True,
            'message': 'Método creado correctamente',
            'method': method.to_dict()
        })

    except Exception as e:
        db.session.rollback()
        logging.error(f"Error al crear método: {str(e)}")
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@bp.route('/admin/api/methods/<int:method_id>', methods=['PUT'])
@admin_required
def update_method(method_id):
    """API: Actualizar método de envío existente"""
    try:
        method = ShippingMethod.query.get(method_id)
        if not method:
            return jsonify({
                'success': False,
                'error': 'Método no encontrado'
            }), 404

        data = request.get_json()

        # Verificar si se está cambiando el código y si ya existe
        if 'code' in data and data['code'] != method.code:
            existing = ShippingMethod.query.filter_by(code=data['code']).first()
            if existing:
                return jsonify({
                    'success': False,
                    'error': f'Ya existe un método con el código "{data["code"]}"'
                }), 400

        # Actualizar campos
        if 'name' in data:
            method.name = data['name']
        if 'code' in data:
            method.code = data['code']
        if 'description' in data:
            method.description = data['description']
        if 'max_km' in data:
            method.max_km = float(data['max_km'])
        if 'is_active' in data:
            method.is_active = data['is_active']

        # Parsear y actualizar horas si se proveen
        if 'start_time' in data:
            from datetime import datetime as dt
            method.start_time = dt.strptime(data['start_time'], '%H:%M').time()
        if 'end_time' in data:
            from datetime import datetime as dt
            method.end_time = dt.strptime(data['end_time'], '%H:%M').time()

        db.session.commit()

        return jsonify({
            'success': True,
            'message': 'Método actualizado correctamente',
            'method': method.to_dict()
        })

    except Exception as e:
        db.session.rollback()
        logging.error(f"Error al actualizar método: {str(e)}")
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@bp.route('/admin/api/methods/<int:method_id>', methods=['DELETE'])
@admin_required
def delete_method(method_id):
    """API: Eliminar método de envío"""
    try:
        method = ShippingMethod.query.get(method_id)
        if not method:
            return jsonify({
                'success': False,
                'error': 'Método no encontrado'
            }), 404

        # Verificar si tiene cotizaciones asociadas
        quotes_count = ShippingQuote.query.filter_by(shipping_method_id=method_id).count()
        if quotes_count > 0:
            return jsonify({
                'success': False,
                'error': f'No se puede eliminar. Hay {quotes_count} cotizaciones asociadas a este método.'
            }), 400

        db.session.delete(method)
        db.session.commit()

        return jsonify({
            'success': True,
            'message': 'Método eliminado correctamente'
        })

    except Exception as e:
        db.session.rollback()
        logging.error(f"Error al eliminar método: {str(e)}")
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@bp.route('/admin/api/methods/<int:method_id>/toggle', methods=['POST'])
@admin_required
def toggle_method_status(method_id):
    """API: Activar/desactivar método de envío"""
    try:
        method = ShippingMethod.query.get(method_id)
        if not method:
            return jsonify({
                'success': False,
                'error': 'Método no encontrado'
            }), 404

        method.is_active = not method.is_active
        db.session.commit()

        status = 'activado' if method.is_active else 'desactivado'
        return jsonify({
            'success': True,
            'message': f'Método {status} correctamente',
            'method': method.to_dict()
        })

    except Exception as e:
        db.session.rollback()
        logging.error(f"Error al cambiar estado del método: {str(e)}")
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500