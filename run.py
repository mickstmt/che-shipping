# run.py
from app import create_app
import os
import sys

# Configurar codificación UTF-8 para Windows
if sys.platform == "win32":
    sys.stdout.reconfigure(encoding='utf-8')

# Crear la aplicación
app = create_app()

if __name__ == '__main__':
    # Obtener configuración del .env
    debug = os.environ.get('FLASK_ENV') == 'development'
    
    print(f"\n{'='*60}")
    print(f"🚀 Iniciando Shipping Service Chile")
    print(f"{'='*60}")
    print(f"🌍 Ambiente: {app.config.get('ENVIRONMENT', 'development').upper()}")
    print(f"🗄️  Base de datos: MySQL")
    print(f"🔧 Debug: {debug}")
    print(f"🌐 URL Local: http://localhost:5000")
    print(f"📦 Panel Envíos: http://localhost:5000/shipping/")
    print(f"🔗 API Quote: http://localhost:5000/shipping/api/quote")
    print(f"{'='*60}")
    print(f"🇨🇱 RouterService integrado para Chile")
    print(f"📍 Dominio producción: envio.chetomi.cl")
    print(f"{'='*60}\n")
    
    app.run(
        host='0.0.0.0',
        port=5000,
        debug=debug
    )
