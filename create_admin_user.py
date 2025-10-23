#!/usr/bin/env python3
"""
Script para crear usuarios administradores
Uso: python create_admin_user.py
"""

from dotenv import load_dotenv
load_dotenv()

from app import create_app, db
from app.models import AdminUser
import getpass
import sys

app = create_app()

def create_admin():
    """Crear un usuario administrador"""

    print("\n" + "="*60)
    print("  CREAR USUARIO ADMINISTRADOR")
    print("="*60)

    # Solicitar username
    while True:
        username = input("\nUsername: ").strip()

        if not username:
            print("[ERROR] El username no puede estar vacío")
            continue

        if len(username) < 3:
            print("[ERROR] El username debe tener al menos 3 caracteres")
            continue

        # Verificar si ya existe
        with app.app_context():
            existing = AdminUser.query.filter_by(username=username).first()
            if existing:
                print(f"[ERROR] Ya existe un usuario con el username '{username}'")
                continue

        break

    # Solicitar password
    while True:
        password = getpass.getpass("Password: ")

        if not password:
            print("[ERROR] El password no puede estar vacío")
            continue

        if len(password) < 6:
            print("[ERROR] El password debe tener al menos 6 caracteres")
            continue

        password_confirm = getpass.getpass("Confirmar password: ")

        if password != password_confirm:
            print("[ERROR] Los passwords no coinciden")
            continue

        break

    # Crear usuario
    with app.app_context():
        admin = AdminUser(username=username)
        admin.set_password(password)

        db.session.add(admin)
        db.session.commit()

        print("\n" + "="*60)
        print(f"[OK] Usuario administrador '{username}' creado exitosamente!")
        print("="*60)
        print(f"\nID: {admin.id}")
        print(f"Username: {admin.username}")
        print(f"Creado: {admin.created_at}")
        print(f"Activo: {'Sí' if admin.is_active else 'No'}")
        print("\n")

def list_admins():
    """Listar usuarios administradores"""

    with app.app_context():
        admins = AdminUser.query.all()

        if not admins:
            print("\n[INFO] No hay usuarios administradores creados")
            return

        print("\n" + "="*60)
        print("  USUARIOS ADMINISTRADORES")
        print("="*60)

        for admin in admins:
            status = "Activo" if admin.is_active else "Inactivo"
            last_login = admin.last_login.strftime("%Y-%m-%d %H:%M") if admin.last_login else "Nunca"

            print(f"\nID: {admin.id}")
            print(f"Username: {admin.username}")
            print(f"Estado: {status}")
            print(f"Último login: {last_login}")
            print(f"Creado: {admin.created_at.strftime('%Y-%m-%d %H:%M')}")
            print("-" * 60)

def disable_admin():
    """Desactivar un usuario administrador"""

    list_admins()

    username = input("\nUsername del admin a desactivar: ").strip()

    with app.app_context():
        admin = AdminUser.query.filter_by(username=username).first()

        if not admin:
            print(f"[ERROR] No existe el usuario '{username}'")
            return

        if not admin.is_active:
            print(f"[INFO] El usuario '{username}' ya está desactivado")
            return

        confirm = input(f"¿Seguro que deseas desactivar '{username}'? (s/n): ")

        if confirm.lower() != 's':
            print("[INFO] Operación cancelada")
            return

        admin.is_active = False
        db.session.commit()

        print(f"[OK] Usuario '{username}' desactivado exitosamente")

def main():
    """Menú principal"""

    while True:
        print("\n" + "="*60)
        print("  GESTIÓN DE USUARIOS ADMINISTRADORES")
        print("="*60)
        print("\n1. Crear nuevo administrador")
        print("2. Listar administradores")
        print("3. Desactivar administrador")
        print("4. Salir")

        choice = input("\nOpción: ").strip()

        if choice == '1':
            create_admin()
        elif choice == '2':
            list_admins()
        elif choice == '3':
            disable_admin()
        elif choice == '4':
            print("\n¡Hasta luego!\n")
            sys.exit(0)
        else:
            print("[ERROR] Opción inválida")

if __name__ == '__main__':
    try:
        main()
    except KeyboardInterrupt:
        print("\n\n[INFO] Operación cancelada por el usuario\n")
        sys.exit(0)
    except Exception as e:
        print(f"\n[ERROR] {str(e)}\n")
        sys.exit(1)
