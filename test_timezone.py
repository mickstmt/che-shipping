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
current_chile = chile_now()
weekday_names = ["Lunes", "Martes", "Miércoles", "Jueves", "Viernes", "Sábado", "Domingo"]
weekday_name = weekday_names[current_chile.weekday()]

print(f"UTC (datetime.utcnow):        {datetime.utcnow()}")
print(f"Server Local (datetime.now):  {datetime.now()}")
print(f"Chile (chile_now):            {current_chile}")
print(f"Chile solo hora:              {chile_time_now()}")
print(f"Día de la semana:             {weekday_name} ({current_chile.weekday()})")

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

        # Determinar días disponibles
        days = []
        if hasattr(method, 'available_monday'):
            if method.available_monday: days.append("Lun")
            if method.available_tuesday: days.append("Mar")
            if method.available_wednesday: days.append("Mié")
            if method.available_thursday: days.append("Jue")
            if method.available_friday: days.append("Vie")
            if method.available_saturday: days.append("Sáb")
            if method.available_sunday: days.append("Dom")
            days_str = ", ".join(days) if days else "Ningún día"
        else:
            days_str = "Todos los días (sin configuración de días)"

        print(f"{method.name}:")
        print(f"  Horario: {method.start_time.strftime('%H:%M')} - {method.end_time.strftime('%H:%M')}")
        print(f"  Días: {days_str}")
        print(f"  Estado: {status}")
        print()

print("="*70)
print(" INFORMACIÓN DE ZONA HORARIA Y DÍAS")
print("="*70)
print("\nChile usa:")
print("  - UTC-3 (horario de verano, octubre-marzo)")
print("  - UTC-4 (horario de invierno, abril-septiembre)")
print("\nLa biblioteca zoneinfo maneja automáticamente el cambio horario.")
print("\nDías de la semana:")
print("  - 0 = Lunes")
print("  - 1 = Martes")
print("  - 2 = Miércoles")
print("  - 3 = Jueves")
print("  - 4 = Viernes")
print("  - 5 = Sábado")
print("  - 6 = Domingo")
print("="*70)
