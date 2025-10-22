#!/usr/bin/env python3
"""
Script de verificacion pre-despliegue
Verifica que todo este configurado correctamente antes de subir a produccion
"""
import os
import sys
from pathlib import Path

def check_files():
    """Verificar que existan los archivos necesarios"""
    required_files = [
        'requirements.txt',
        '.gitignore',
        '.env.example',
        'run.py',
        'config.py',
        'gunicorn_config.py',
        'README.md',
        'DEPLOYMENT.md',
        'deployment/shipping-service.service',
        'deployment/nginx-config',
        'database/init.sql'
    ]

    print("Verificando archivos necesarios...")
    missing = []
    for file in required_files:
        if not Path(file).exists():
            missing.append(file)
            print(f"  [X] Falta: {file}")
        else:
            print(f"  [OK] {file}")

    return len(missing) == 0

def check_env_example():
    """Verificar que .env.example no tenga datos sensibles"""
    print("\nVerificando .env.example...")

    if not Path('.env.example').exists():
        print("  [X] .env.example no existe")
        return False

    with open('.env.example', 'r', encoding='utf-8') as f:
        content = f.read()

    sensitive_patterns = [
        'Bp2pvtMX',  # Password real
        'eyJvcmciOiI1YjNjZTM',  # API key real
        'mi-clave-secreta-para-desarrollo'  # Secret key real
    ]

    has_sensitive = False
    for pattern in sensitive_patterns:
        if pattern in content:
            print(f"  [!] ALERTA: .env.example contiene datos sensibles: {pattern[:10]}...")
            has_sensitive = True

    if not has_sensitive:
        print("  [OK] .env.example esta limpio")

    return not has_sensitive

def check_gitignore():
    """Verificar que .gitignore este configurado correctamente"""
    print("\nVerificando .gitignore...")

    if not Path('.gitignore').exists():
        print("  [X] .gitignore no existe")
        return False

    with open('.gitignore', 'r', encoding='utf-8') as f:
        content = f.read()

    required_patterns = ['.env', '__pycache__', '*.pyc', 'venv/']
    missing = []

    for pattern in required_patterns:
        if pattern not in content:
            missing.append(pattern)
            print(f"  [X] Falta patron: {pattern}")
        else:
            print(f"  [OK] {pattern}")

    return len(missing) == 0

def check_sensitive_files():
    """Verificar que no se suban archivos sensibles"""
    print("\nVerificando que archivos sensibles no esten en el repo...")

    sensitive_files = [
        '.env',
        'diagnostico.py',
        'test_coords.py',
        'test_route.py'
    ]

    found = []
    for file in sensitive_files:
        if Path(file).exists():
            # Verificar si esta en .gitignore
            with open('.gitignore', 'r', encoding='utf-8') as f:
                gitignore = f.read()

            if file not in gitignore and not any(pattern in gitignore for pattern in ['*.py', 'test_*']):
                found.append(file)
                print(f"  [!] ALERTA: {file} existe y podria subirse a Git")
            else:
                print(f"  [OK] {file} esta en .gitignore")

    return len(found) == 0

def main():
    print("="*70)
    print("VERIFICACION PRE-DESPLIEGUE")
    print("="*70)
    print()

    checks = [
        ("Archivos necesarios", check_files()),
        (".env.example limpio", check_env_example()),
        (".gitignore configurado", check_gitignore()),
        ("Archivos sensibles protegidos", check_sensitive_files())
    ]

    print("\n" + "="*70)
    print("RESUMEN")
    print("="*70)

    all_passed = True
    for name, passed in checks:
        status = "[OK]" if passed else "[FAIL]"
        print(f"{status} - {name}")
        if not passed:
            all_passed = False

    print("="*70)

    if all_passed:
        print("\n[OK] TODO LISTO PARA DESPLEGAR")
        print("\nProximos pasos:")
        print("1. git add .")
        print("2. git commit -m 'Preparado para produccion'")
        print("3. git push origin main")
        print("4. Seguir guia en DEPLOYMENT.md")
        return 0
    else:
        print("\n[ERROR] CORRIGE LOS ERRORES ANTES DE DESPLEGAR")
        return 1

if __name__ == '__main__':
    sys.exit(main())
