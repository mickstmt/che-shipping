#!/usr/bin/env python3
"""
Script para crear el primer usuario admin automáticamente
Username: admin
Password: admin123
"""

from dotenv import load_dotenv
load_dotenv()

from app import create_app, db
from app.models import AdminUser

app = create_app()

with app.app_context():
    # Verificar si ya existe
    existing = AdminUser.query.filter_by(username='admin').first()

    if existing:
        print("[INFO] Ya existe un usuario 'admin'")
        print(f"Creado: {existing.created_at}")
        print(f"Último login: {existing.last_login or 'Nunca'}")
    else:
        # Crear usuario admin por defecto
        admin = AdminUser(username='admin')
        admin.set_password('admin123')

        db.session.add(admin)
        db.session.commit()

        print("="*60)
        print("[OK] Usuario administrador creado!")
        print("="*60)
        print(f"Username: admin")
        print(f"Password: admin123")
        print(f"\nPuedes iniciar sesión en: http://localhost:5000/shipping/login")
        print("\nIMPORTANTE: Cambia la contraseña después del primer login")
        print("="*60)
