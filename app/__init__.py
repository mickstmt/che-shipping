# app/__init__.py
from flask import Flask, redirect, url_for, request, render_template
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager
import os

# Inicializar extensiones
db = SQLAlchemy()
login_manager = LoginManager()

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

    # Configurar Flask-Login
    login_manager.init_app(app)
    login_manager.login_view = 'shipping.login'
    login_manager.login_message = 'Por favor inicia sesión para acceder a esta página.'
    login_manager.login_message_category = 'warning'

    @login_manager.user_loader
    def load_user(user_id):
        from app.models import AdminUser
        return AdminUser.query.get(int(user_id))

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

    # Auto-migración: Agregar columnas de días de la semana si no existen
    with app.app_context():
        try:
            from sqlalchemy import text, inspect
            inspector = inspect(db.engine)

            # Verificar si existe la tabla shipping_methods
            if 'shipping_methods' in inspector.get_table_names():
                columns = [col['name'] for col in inspector.get_columns('shipping_methods')]

                # Si no existe la columna available_monday, agregar todas las columnas de días
                if 'available_monday' not in columns:
                    print("⚙️  Agregando columnas de días de la semana...")
                    db.session.execute(text("""
                        ALTER TABLE shipping_methods
                        ADD COLUMN available_monday BOOLEAN DEFAULT TRUE,
                        ADD COLUMN available_tuesday BOOLEAN DEFAULT TRUE,
                        ADD COLUMN available_wednesday BOOLEAN DEFAULT TRUE,
                        ADD COLUMN available_thursday BOOLEAN DEFAULT TRUE,
                        ADD COLUMN available_friday BOOLEAN DEFAULT TRUE,
                        ADD COLUMN available_saturday BOOLEAN DEFAULT TRUE,
                        ADD COLUMN available_sunday BOOLEAN DEFAULT TRUE
                    """))
                    db.session.commit()
                    print("✓ Columnas de días agregadas")

                    # Configurar "Envío Hoy" para lunes a viernes
                    print("⚙️  Configurando 'Envío Hoy' para lunes a viernes...")
                    db.session.execute(text("""
                        UPDATE shipping_methods
                        SET available_saturday = FALSE,
                            available_sunday = FALSE
                        WHERE code = 'envio_hoy'
                    """))
                    db.session.commit()
                    print("✓ 'Envío Hoy' configurado para lunes a viernes")
        except Exception as e:
            print(f"⚠️  Error en auto-migración: {e}")
            db.session.rollback()

    return app
