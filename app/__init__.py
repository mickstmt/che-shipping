# app/__init__.py
from flask import Flask, redirect, url_for, request, render_template
from flask_sqlalchemy import SQLAlchemy
import os

# Inicializar extensiones
db = SQLAlchemy()

def create_app(config_name=None):
    """Factory para crear la aplicación Flask"""

    if config_name is None:
        config_name = os.environ.get('ENVIRONMENT', 'development')

    # Configurar template_folder para usar templates en la raíz del proyecto
    import os as os_module
    template_dir = os_module.path.abspath(os_module.path.join(os_module.path.dirname(__file__), '..', 'templates'))

    app = Flask(__name__, template_folder=template_dir)
    
    # Configuración básica
    from config import config
    app.config.from_object(config[config_name])
    
    # Inicializar extensiones
    db.init_app(app)
    
    # ========================================
    # MANEJAR RECONEXIÓN DE BD
    # ========================================
    @app.teardown_appcontext
    def shutdown_session(exception=None):
        """Cerrar sesión de BD al final de cada request"""
        db.session.remove()
    
    # Registrar blueprints
    from app.routes import shipping
    app.register_blueprint(shipping.bp)
    
    # Contexto global para templates
    @app.context_processor
    def inject_config():
        return {
            'environment': app.config.get('ENVIRONMENT', 'development'),
            'is_production': app.config.get('ENVIRONMENT') == 'production'
        }
    
    # Ruta principal
    @app.route('/')
    def index():
        """Dashboard principal"""
        return render_template('base.html')
    
    return app
