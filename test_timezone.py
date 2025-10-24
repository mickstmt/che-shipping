#!/usr/bin/env python3
"""
Script para verificar zona horaria de Chile
"""

from dotenv import load_dotenv
load_dotenv()

from app import create_app
from app.models import chile_now, chile_time_now, ShippingMethod
from datetime import datetime

app = create_app()

print("="*70)
print(" VERIFICACIÓN DE ZONA HORARIA - CHILE")
print("="*70)

# Hora actual en diferentes zonas
print("\n[1] Horas Actuales:")
print("-" * 70)
print(f"UTC (datetime.utcnow):        {datetime.utcnow()}")
print(f"Server Local (datetime.now):  {datetime.now()}")
print(f"Chile (chile_now):            {chile_now()}")
print(f"Chile solo hora:              {chile_time_now()}")

# Verificar métodos de envío
with app.app_context():
    methods = ShippingMethod.query.all()

    print("\n[2] Disponibilidad de Métodos de Envío:")
    print("-" * 70)

    chile_time = chile_time_now()
    print(f"Hora actual en Chile: {chile_time.strftime('%H:%M:%S')}")
    print()

    for method in methods:
        available = method.is_available_now()
        status = "[DISPONIBLE]" if available else "[NO DISPONIBLE]"

        print(f"{method.name}:")
        print(f"  Horario: {method.start_time.strftime('%H:%M')} - {method.end_time.strftime('%H:%M')}")
        print(f"  Estado: {status}")
        print()

print("="*70)
print(" INFORMACIÓN DE ZONA HORARIA")
print("="*70)
print("\nChile usa:")
print("  - UTC-3 (horario de verano, octubre-marzo)")
print("  - UTC-4 (horario de invierno, abril-septiembre)")
print("\nLa biblioteca zoneinfo maneja automáticamente el cambio horario.")
print("="*70)
