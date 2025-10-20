from flask import Blueprint, request, jsonify, render_template
from flask_login import login_required, current_user
from app import db
from app.models import ShippingZone, ShippingMethod, ShippingQuote
from app.routes.auth import admin_required
from app.services.router_service import router_service
from datetime import datetime, time
import json
import logging

bp = Blueprint('shipping', __name__, url_prefix='/shipping')

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
    
    POST /shipping/api/test-address
    {
        "address": "Providencia, Santiago, Chile"
    }
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
@login_required
def index():
    """Panel principal de gestión de envíos"""
    return render_template('shipping/index.html', title='Gestión de Envíos')

@bp.route('/admin/methods')
@login_required
@admin_required
def manage_methods():
    """Gestión de métodos de envío"""
    methods = ShippingMethod.query.all()
    return render_template('shipping/methods.html', methods=methods, title='Métodos de Envío')

@bp.route('/admin/zones')
@login_required
@admin_required
def manage_zones():
    """Gestión de zonas de envío"""
    zones = ShippingZone.query.order_by(ShippingZone.min_km).all()
    return render_template('shipping/zones.html', zones=zones, title='Zonas de Envío')

@bp.route('/admin/quotes')
@login_required
def view_quotes():
    """Ver cotizaciones realizadas"""
    page = request.args.get('page', 1, type=int)
    quotes = ShippingQuote.query.order_by(ShippingQuote.created_at.desc()).paginate(
        page=page, per_page=50, error_out=False
    )
    return render_template('shipping/quotes.html', quotes=quotes, title='Cotizaciones')

# ========================================
# API CRUD PARA ADMIN
# ========================================

@bp.route('/admin/api/methods', methods=['GET'])
@login_required
@admin_required
def api_get_methods():
    """API: Obtener métodos de envío"""
    methods = ShippingMethod.query.all()
    return jsonify({
        'success': True,
        'methods': [method.to_dict() for method in methods]
    })

@bp.route('/admin/api/methods', methods=['POST'])
@login_required
@admin_required
def api_create_method():
    """API: Crear método de envío"""
    try:
        data = request.get_json()
        
        # Validaciones
        required_fields = ['name', 'code', 'start_time', 'end_time']
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
                'error': f'Ya existe un método con el código: {data["code"]}'
            }), 400
        
        method = ShippingMethod(
            name=data['name'],
            code=data['code'],
            description=data.get('description', ''),
            start_time=datetime.strptime(data['start_time'], '%H:%M').time(),
            end_time=datetime.strptime(data['end_time'], '%H:%M').time(),
            max_km=float(data.get('max_km', 7.0)),
            is_active=data.get('is_active', True)
        )
        
        db.session.add(method)
        db.session.commit()
        
        return jsonify({
            'success': True,
            'method': method.to_dict(),
            'message': 'Método de envío creado correctamente'
        })
        
    except Exception as e:
        db.session.rollback()
        return jsonify({
            'success': False,
            'error': str(e)
        }), 400

@bp.route('/admin/api/methods/<int:method_id>', methods=['PUT'])
@login_required
@admin_required
def api_update_method(method_id):
    """API: Actualizar método de envío"""
    try:
        method = ShippingMethod.query.get_or_404(method_id)
        data = request.get_json()
        
        # Verificar código único si se está cambiando
        if 'code' in data and data['code'] != method.code:
            existing = ShippingMethod.query.filter_by(code=data['code']).first()
            if existing:
                return jsonify({
                    'success': False,
                    'error': f'Ya existe un método con el código: {data["code"]}'
                }), 400
        
        method.name = data.get('name', method.name)
        method.code = data.get('code', method.code)
        method.description = data.get('description', method.description)
        
        if 'start_time' in data:
            method.start_time = datetime.strptime(data['start_time'], '%H:%M').time()
        if 'end_time' in data:
            method.end_time = datetime.strptime(data['end_time'], '%H:%M').time()
        
        method.max_km = float(data.get('max_km', method.max_km))
        method.is_active = data.get('is_active', method.is_active)
        method.updated_at = datetime.utcnow()
        
        db.session.commit()
        
        return jsonify({
            'success': True,
            'method': method.to_dict(),
            'message': 'Método actualizado correctamente'
        })
        
    except Exception as e:
        db.session.rollback()
        return jsonify({
            'success': False,
            'error': str(e)
        }), 400

@bp.route('/admin/api/zones', methods=['GET'])
@login_required
@admin_required
def api_get_zones():
    """API: Obtener zonas de envío"""
    zones = ShippingZone.query.order_by(ShippingZone.min_km).all()
    return jsonify({
        'success': True,
        'zones': [zone.to_dict() for zone in zones]
    })

@bp.route('/admin/api/zones', methods=['POST'])
@login_required
@admin_required
def api_create_zone():
    """API: Crear zona de envío"""
    try:
        data = request.get_json()
        
        # Validaciones
        required_fields = ['min_km', 'max_km', 'price_clp']
        for field in required_fields:
            if field not in data:
                return jsonify({
                    'success': False,
                    'error': f'Campo requerido: {field}'
                }), 400
        
        min_km = float(data['min_km'])
        max_km = float(data['max_km'])
        price_clp = int(data['price_clp'])
        
        # Validaciones de lógica
        if min_km >= max_km:
            return jsonify({
                'success': False,
                'error': 'El kilometraje mínimo debe ser menor que el máximo'
            }), 400
        
        if price_clp <= 0:
            return jsonify({
                'success': False,
                'error': 'El precio debe ser mayor a 0'
            }), 400
        
        # Verificar que no se solape con otra zona
        overlapping = ShippingZone.query.filter(
            ShippingZone.is_active == True,
            db.or_(
                db.and_(ShippingZone.min_km <= min_km, ShippingZone.max_km > min_km),
                db.and_(ShippingZone.min_km < max_km, ShippingZone.max_km >= max_km),
                db.and_(ShippingZone.min_km >= min_km, ShippingZone.max_km <= max_km)
            )
        ).first()
        
        if overlapping:
            return jsonify({
                'success': False,
                'error': f'La zona se solapa con la zona existente: {overlapping.min_km}-{overlapping.max_km} km'
            }), 400
        
        zone = ShippingZone(
            min_km=min_km,
            max_km=max_km,
            price_clp=price_clp,
            is_active=data.get('is_active', True)
        )
        
        db.session.add(zone)
        db.session.commit()
        
        return jsonify({
            'success': True,
            'zone': zone.to_dict(),
            'message': 'Zona de envío creada correctamente'
        })
        
    except Exception as e:
        db.session.rollback()
        return jsonify({
            'success': False,
            'error': str(e)
        }), 400

@bp.route('/admin/api/zones/<int:zone_id>', methods=['PUT'])
@login_required
@admin_required
def api_update_zone(zone_id):
    """API: Actualizar zona de envío"""
    try:
        zone = ShippingZone.query.get_or_404(zone_id)
        data = request.get_json()
        
        min_km = float(data.get('min_km', zone.min_km))
        max_km = float(data.get('max_km', zone.max_km))
        price_clp = int(data.get('price_clp', zone.price_clp))
        
        # Validaciones de lógica
        if min_km >= max_km:
            return jsonify({
                'success': False,
                'error': 'El kilometraje mínimo debe ser menor que el máximo'
            }), 400
        
        if price_clp <= 0:
            return jsonify({
                'success': False,
                'error': 'El precio debe ser mayor a 0'
            }), 400
        
        # Verificar solapamiento con otras zonas (excluyendo la actual)
        overlapping = ShippingZone.query.filter(
            ShippingZone.id != zone_id,
            ShippingZone.is_active == True,
            db.or_(
                db.and_(ShippingZone.min_km <= min_km, ShippingZone.max_km > min_km),
                db.and_(ShippingZone.min_km < max_km, ShippingZone.max_km >= max_km),
                db.and_(ShippingZone.min_km >= min_km, ShippingZone.max_km <= max_km)
            )
        ).first()
        
        if overlapping:
            return jsonify({
                'success': False,
                'error': f'La zona se solapa con la zona existente: {overlapping.min_km}-{overlapping.max_km} km'
            }), 400
        
        zone.min_km = min_km
        zone.max_km = max_km
        zone.price_clp = price_clp
        zone.is_active = data.get('is_active', zone.is_active)
        zone.updated_at = datetime.utcnow()
        
        db.session.commit()
        
        return jsonify({
            'success': True,
            'zone': zone.to_dict(),
            'message': 'Zona actualizada correctamente'
        })
        
    except Exception as e:
        db.session.rollback()
        return jsonify({
            'success': False,
            'error': str(e)
        }), 400

@bp.route('/admin/api/zones/<int:zone_id>', methods=['DELETE'])
@login_required
@admin_required
def api_delete_zone(zone_id):
    """API: Eliminar zona de envío"""
    try:
        zone = ShippingZone.query.get_or_404(zone_id)
        
        # Verificar si hay cotizaciones usando esta zona
        quotes_count = ShippingQuote.query.filter_by(zone_id=zone_id).count()
        
        if quotes_count > 0:
            return jsonify({
                'success': False,
                'error': f'No se puede eliminar la zona porque tiene {quotes_count} cotizaciones asociadas. Desactívala en su lugar.'
            }), 400
        
        db.session.delete(zone)
        db.session.commit()
        
        return jsonify({
            'success': True,
            'message': 'Zona eliminada correctamente'
        })
        
    except Exception as e:
        db.session.rollback()
        return jsonify({
            'success': False,
            'error': str(e)
        }), 400

@bp.route('/admin/api/quotes/stats', methods=['GET'])
@login_required
def api_quotes_stats():
    """API: Estadísticas de cotizaciones"""
    try:
        from datetime import date, timedelta
        
        today = date.today()
        yesterday = today - timedelta(days=1)
        week_ago = today - timedelta(days=7)
        
        # Cotizaciones de hoy
        today_quotes = ShippingQuote.query.filter(
            db.func.date(ShippingQuote.created_at) == today
        ).count()
        
        # Cotizaciones de ayer
        yesterday_quotes = ShippingQuote.query.filter(
            db.func.date(ShippingQuote.created_at) == yesterday
        ).count()
        
        # Cotizaciones de la semana
        week_quotes = ShippingQuote.query.filter(
            ShippingQuote.created_at >= week_ago
        ).count()
        
        # Total de cotizaciones
        total_quotes = ShippingQuote.query.count()
        
        # Métodos más usados
        method_stats = db.session.query(
            ShippingMethod.name,
            db.func.count(ShippingQuote.id).label('count')
        ).join(ShippingQuote).group_by(ShippingMethod.id).all()
        
        # Zonas más usadas
        zone_stats = db.session.query(
            ShippingZone.min_km,
            ShippingZone.max_km,
            ShippingZone.price_clp,
            db.func.count(ShippingQuote.id).label('count')
        ).join(ShippingQuote).group_by(ShippingZone.id).all()
        
        return jsonify({
            'success': True,
            'stats': {
                'today_quotes': today_quotes,
                'yesterday_quotes': yesterday_quotes,
                'week_quotes': week_quotes,
                'total_quotes': total_quotes,
                'method_stats': [
                    {'method': stat[0], 'count': stat[1]} 
                    for stat in method_stats
                ],
                'zone_stats': [
                    {
                        'range': f'{stat[0]}-{stat[1]} km',
                        'price': stat[2],
                        'count': stat[3]
                    } for stat in zone_stats
                ]
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
@login_required
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
        
        # Crear zonas de envío por defecto (según especificaciones)
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

@bp.route('/admin/api/reset-data', methods=['POST'])
@login_required
@admin_required
def reset_data():
    """API: Resetear todos los datos del sistema"""
    try:
        # Eliminar todas las cotizaciones primero (por foreign keys)
        ShippingQuote.query.delete()
        
        # Eliminar métodos y zonas
        ShippingMethod.query.delete()
        ShippingZone.query.delete()
        
        db.session.commit()
        
        return jsonify({
            'success': True,
            'message': 'Todos los datos han sido eliminados. Puedes inicializar datos por defecto ahora.'
        })
        
    except Exception as e:
        db.session.rollback()
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500
