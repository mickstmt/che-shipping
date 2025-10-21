# init_db.py
"""
Script para inicializar la base de datos y crear las tablas
"""
import sys

# Configurar codificación UTF-8 para Windows
if sys.platform == "win32":
    sys.stdout.reconfigure(encoding='utf-8')

from app import create_app, db
from app.models import ShippingZone, ShippingMethod, ShippingQuote
from datetime import time

def init_database():
    """Crear todas las tablas en la base de datos"""
    app = create_app()

    with app.app_context():
        print("Creando tablas en la base de datos...")

        # Crear todas las tablas
        db.create_all()

        print("✓ Tablas creadas exitosamente")

        # Verificar si ya existen datos
        if ShippingMethod.query.count() > 0 or ShippingZone.query.count() > 0:
            print("\n⚠️  Ya existen datos en la base de datos.")
            print("   Si deseas reinicializar, elimina los datos primero.")
            return

        print("\nInicializando datos por defecto...")

        # Crear métodos de envío
        methods = [
            ShippingMethod(
                name='Envío Hoy',
                code='envio_hoy',
                description='Entrega el mismo día (disponible hasta las 18:00)',
                start_time=time(0, 1),   # 00:01
                end_time=time(18, 0),    # 18:00
                max_km=7.0,
                is_active=True
            ),
            ShippingMethod(
                name='Envío Programado',
                code='envio_programado',
                description='Entrega programada para el día siguiente',
                start_time=time(0, 0),   # 00:00
                end_time=time(23, 59),   # 23:59
                max_km=7.0,
                is_active=True
            )
        ]

        for method in methods:
            db.session.add(method)
            print(f"  ✓ Método creado: {method.name}")

        # Crear zonas de envío
        zones = [
            ShippingZone(min_km=0.0, max_km=3.0, price_clp=3500, is_active=True),
            ShippingZone(min_km=3.0, max_km=4.0, price_clp=4500, is_active=True),
            ShippingZone(min_km=4.0, max_km=5.0, price_clp=5000, is_active=True),
            ShippingZone(min_km=5.0, max_km=6.0, price_clp=5500, is_active=True),
            ShippingZone(min_km=6.0, max_km=7.0, price_clp=6500, is_active=True)
        ]

        for zone in zones:
            db.session.add(zone)
            print(f"  ✓ Zona creada: {zone.min_km}-{zone.max_km} km → ${zone.price_clp:,}")

        # Guardar cambios
        db.session.commit()

        print("\n" + "="*60)
        print("✓ Base de datos inicializada correctamente")
        print("="*60)
        print(f"\nMétodos de envío creados: {len(methods)}")
        print(f"Zonas de tarifas creadas: {len(zones)}")
        print("\nPuedes iniciar el servidor con: python run.py")
        print("="*60)

if __name__ == '__main__':
    init_database()
