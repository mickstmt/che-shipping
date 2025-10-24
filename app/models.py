from app import db
from datetime import datetime, time, timedelta
import json

try:
    from zoneinfo import ZoneInfo
    CHILE_TZ = ZoneInfo("America/Santiago")
    USE_ZONEINFO = True
except (ImportError, Exception):
    # Fallback para Windows sin tzdata
    USE_ZONEINFO = False
    CHILE_UTC_OFFSET = -3  # UTC-3 (horario de verano Chile)

def chile_now():
    """Obtener fecha/hora actual en zona horaria de Chile"""
    if USE_ZONEINFO:
        return datetime.now(CHILE_TZ)
    else:
        # Fallback: UTC + offset de Chile
        return datetime.utcnow() + timedelta(hours=CHILE_UTC_OFFSET)

def chile_time_now():
    """Obtener solo la hora actual en zona horaria de Chile"""
    return chile_now().time()

# AGREGAR ESTOS MODELOS AL FINAL DE app/models.py

class ShippingZone(db.Model):
    """Modelo para zonas de envío por kilometraje"""
    __tablename__ = 'shipping_zones'
    
    id = db.Column(db.Integer, primary_key=True)
    min_km = db.Column(db.Float, nullable=False)
    max_km = db.Column(db.Float, nullable=False)
    price_clp = db.Column(db.Integer, nullable=False)  # Precio en pesos chilenos
    is_active = db.Column(db.Boolean, default=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    def __repr__(self):
        return f'<ShippingZone {self.min_km}-{self.max_km}km: ${self.price_clp:,}>'
    
    def to_dict(self):
        return {
            'id': self.id,
            'min_km': self.min_km,
            'max_km': self.max_km,
            'price_clp': self.price_clp,
            'price_formatted': f'${self.price_clp:,}',
            'range_text': f'{self.min_km}-{self.max_km} km',
            'is_active': self.is_active,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'updated_at': self.updated_at.isoformat() if self.updated_at else None
        }

class ShippingMethod(db.Model):
    """Modelo para métodos de envío"""
    __tablename__ = 'shipping_methods'
    
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    code = db.Column(db.String(50), unique=True, nullable=False)
    description = db.Column(db.Text)
    is_active = db.Column(db.Boolean, default=True)
    start_time = db.Column(db.Time, nullable=False)  # Hora de inicio
    end_time = db.Column(db.Time, nullable=False)    # Hora de fin
    max_km = db.Column(db.Float, default=7.0)        # Distancia máxima
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    def __repr__(self):
        return f'<ShippingMethod {self.name}>'
    
    def is_available_now(self):
        """Verificar si el método está disponible en este momento (hora de Chile)"""
        if not self.is_active:
            return False

        now = chile_time_now()  # Usar hora de Chile
        
        # Si es el mismo día (start_time <= end_time)
        if self.start_time <= self.end_time:
            return self.start_time <= now <= self.end_time
        # Si cruza medianoche (start_time > end_time)
        else:
            return now >= self.start_time or now <= self.end_time
    
    def to_dict(self):
        return {
            'id': self.id,
            'name': self.name,
            'code': self.code,
            'description': self.description,
            'is_active': self.is_active,
            'start_time': self.start_time.strftime('%H:%M') if self.start_time else None,
            'end_time': self.end_time.strftime('%H:%M') if self.end_time else None,
            'max_km': self.max_km,
            'is_available_now': self.is_available_now(),
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'updated_at': self.updated_at.isoformat() if self.updated_at else None
        }

class ShippingQuote(db.Model):
    """Modelo para cotizaciones de envío"""
    __tablename__ = 'shipping_quotes'
    
    id = db.Column(db.Integer, primary_key=True)
    session_id = db.Column(db.String(100))  # Para identificar sesión de Jumpseller
    origin_address = db.Column(db.Text)
    destination_address = db.Column(db.Text, nullable=False)
    origin_lat = db.Column(db.Float)        # Latitud origen
    origin_lng = db.Column(db.Float)        # Longitud origen
    destination_lat = db.Column(db.Float)   # Latitud destino
    destination_lng = db.Column(db.Float)   # Longitud destino
    distance_km = db.Column(db.Float, nullable=False)
    duration_minutes = db.Column(db.Integer) # Tiempo de viaje estimado
    shipping_method_id = db.Column(db.Integer, db.ForeignKey('shipping_methods.id'))
    zone_id = db.Column(db.Integer, db.ForeignKey('shipping_zones.id'))
    price_clp = db.Column(db.Integer, nullable=False)
    is_available = db.Column(db.Boolean, default=True)
    router_response = db.Column(db.Text)  # Respuesta completa de RouterService
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    # Relaciones
    shipping_method = db.relationship('ShippingMethod', backref='quotes')
    zone = db.relationship('ShippingZone', backref='quotes')
    
    def __repr__(self):
        return f'<ShippingQuote {self.distance_km}km: ${self.price_clp:,}>'
    
    def to_dict(self):
        return {
            'id': self.id,
            'session_id': self.session_id,
            'origin_address': self.origin_address,
            'destination_address': self.destination_address,
            'distance_km': self.distance_km,
            'duration_minutes': self.duration_minutes,
            'shipping_method': self.shipping_method.to_dict() if self.shipping_method else None,
            'zone': self.zone.to_dict() if self.zone else None,
            'price_clp': self.price_clp,
            'price_formatted': f'${self.price_clp:,}',
            'is_available': self.is_available,
            'router_response': json.loads(self.router_response) if self.router_response else None,
            'created_at': self.created_at.isoformat() if self.created_at else None
        }


class AdminUser(db.Model):
    """Modelo para usuarios administradores del sistema"""
    __tablename__ = 'admin_users'

    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(50), unique=True, nullable=False)
    password_hash = db.Column(db.String(255), nullable=False)
    is_active = db.Column(db.Boolean, default=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    last_login = db.Column(db.DateTime)

    def __repr__(self):
        return f'<AdminUser {self.username}>'

    def set_password(self, password):
        """Hashear y guardar password"""
        from werkzeug.security import generate_password_hash
        self.password_hash = generate_password_hash(password)

    def check_password(self, password):
        """Verificar password"""
        from werkzeug.security import check_password_hash
        return check_password_hash(self.password_hash, password)

    # Flask-Login integration
    @property
    def is_authenticated(self):
        return True

    @property
    def is_anonymous(self):
        return False

    def get_id(self):
        return str(self.id)
