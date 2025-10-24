#!/usr/bin/env python3
"""
Script para agregar columnas de días de la semana a la tabla shipping_methods
"""

from dotenv import load_dotenv
load_dotenv()

from app import create_app, db
from sqlalchemy import text

app = create_app()

with app.app_context():
    print("=" * 70)
    print(" AGREGANDO COLUMNAS DE DÍAS DE LA SEMANA")
    print("=" * 70)
    print()

    # Verificar si las columnas ya existen
    result = db.session.execute(text("SHOW COLUMNS FROM shipping_methods LIKE 'available_monday'"))
    if result.fetchone():
        print("✓ Las columnas ya existen en la base de datos.")
        print()
    else:
        print("[1] Agregando columnas a la tabla shipping_methods...")

        try:
            # Agregar columnas de días de la semana (todas por defecto en TRUE)
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
            print("✓ Columnas agregadas exitosamente.")
            print()
        except Exception as e:
            print(f"✗ Error al agregar columnas: {e}")
            db.session.rollback()
            print()

    # Configurar "Envío Hoy" para que solo esté disponible de lunes a viernes
    print("[2] Configurando 'Envío Hoy' para lunes a viernes...")

    try:
        db.session.execute(text("""
            UPDATE shipping_methods
            SET available_saturday = FALSE,
                available_sunday = FALSE
            WHERE code = 'envio_hoy'
        """))
        db.session.commit()
        print("✓ 'Envío Hoy' configurado para lunes a viernes únicamente.")
        print()
    except Exception as e:
        print(f"✗ Error al configurar días: {e}")
        db.session.rollback()
        print()

    # Mostrar configuración actual
    print("[3] Configuración actual de métodos de envío:")
    print("-" * 70)

    result = db.session.execute(text("""
        SELECT name, code,
               available_monday, available_tuesday, available_wednesday,
               available_thursday, available_friday, available_saturday,
               available_sunday
        FROM shipping_methods
    """))

    for row in result:
        name, code, mon, tue, wed, thu, fri, sat, sun = row
        days = []
        if mon: days.append("Lun")
        if tue: days.append("Mar")
        if wed: days.append("Mié")
        if thu: days.append("Jue")
        if fri: days.append("Vie")
        if sat: days.append("Sáb")
        if sun: days.append("Dom")

        days_str = ", ".join(days) if days else "Ningún día"

        print(f"\n{name} ({code}):")
        print(f"  Días disponibles: {days_str}")

    print()
    print("=" * 70)
    print(" MIGRACIÓN COMPLETADA")
    print("=" * 70)
