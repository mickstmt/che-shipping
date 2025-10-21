# config.py
import os
from dotenv import load_dotenv
from urllib.parse import quote_plus

# Cargar variables de entorno
load_dotenv()

class Config:
    """Configuración base"""
    SECRET_KEY = os.environ.get('SECRET_KEY') or 'dev-key-change-this-in-production'
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    
    # Configuración de sesión
    SESSION_COOKIE_SECURE = False
    SESSION_COOKIE_HTTPONLY = True
    PERMANENT_SESSION_LIFETIME = 3600
    
    # Pool de conexiones optimizado
    SQLALCHEMY_ENGINE_OPTIONS = {
        'pool_size': 10,
        'pool_recycle': 3600,
        'pool_pre_ping': True,
        'max_overflow': 20,
        'pool_timeout': 30,
        'connect_args': {
            'connect_timeout': 10,
            'read_timeout': 30,
            'write_timeout': 30
        }
    }

class DevelopmentConfig(Config):
    """Configuración para desarrollo local"""
    DEBUG = True
    ENVIRONMENT = 'development'
    
    # Base de datos local
    db_user = os.environ.get('DB_USER') or 'root'
    db_password = os.environ.get('DB_PASSWORD') or ''
    db_host = os.environ.get('DB_HOST') or 'localhost'
    db_name = os.environ.get('DB_NAME') or 'shipping_chile'
    
    if db_password:
        encoded_password = quote_plus(db_password)
        SQLALCHEMY_DATABASE_URI = f"mysql+pymysql://{db_user}:{encoded_password}@{db_host}/{db_name}"
    else:
        SQLALCHEMY_DATABASE_URI = f"mysql+pymysql://{db_user}@{db_host}/{db_name}"

class ProductionConfig(Config):
    """Configuración para producción"""
    DEBUG = False
    ENVIRONMENT = 'production'
    SESSION_COOKIE_SECURE = True
    
    # Variables para producción (opcional, no validar si no están)
    db_user = os.environ.get('DB_USER', 'root')
    db_password = os.environ.get('DB_PASSWORD', '')
    db_host = os.environ.get('DB_HOST', 'localhost')
    db_name = os.environ.get('DB_NAME_PRODUCTION') or os.environ.get('DB_NAME', 'shipping_chile')
    
    if db_password:
        encoded_password = quote_plus(db_password)
        SQLALCHEMY_DATABASE_URI = f"mysql+pymysql://{db_user}:{encoded_password}@{db_host}/{db_name}"
    else:
        SQLALCHEMY_DATABASE_URI = f"mysql+pymysql://{db_user}@{db_host}/{db_name}"

# Diccionario de configuraciones
config = {
    'development': DevelopmentConfig,
    'production': ProductionConfig,
    'default': DevelopmentConfig
}