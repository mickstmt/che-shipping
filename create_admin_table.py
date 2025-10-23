#!/usr/bin/env python3
"""
Script para crear la tabla admin_users en la base de datos
"""

from dotenv import load_dotenv
load_dotenv()  # Cargar variables de entorno

from app import create_app, db
from app.models import AdminUser

app = create_app()

with app.app_context():
    print("Creando tabla admin_users...")
    db.create_all()
    print("[OK] Tabla admin_users creada exitosamente!")
