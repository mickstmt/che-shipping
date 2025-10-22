#!/usr/bin/env python3
"""
Script de diagnóstico para Google Maps API
Identifica el problema exacto con la configuración
"""

import os
import sys
import requests
from dotenv import load_dotenv

# Cargar variables de entorno
load_dotenv()

API_KEY = os.environ.get('GOOGLE_MAPS_API_KEY')

print("="*70)
print(" DIAGNÓSTICO DE GOOGLE MAPS API")
print("="*70)

# 1. Verificar que existe la API Key
print("\n[1] Verificando API Key...")
if not API_KEY or API_KEY == 'tu_google_maps_api_key_aqui':
    print("  [X] ERROR: API Key no configurada")
    sys.exit(1)
else:
    print(f"  [OK] API Key configurada: {API_KEY[:20]}...")

# 2. Probar Geocoding API directamente
print("\n[2] Probando Geocoding API (HTTP directo)...")
geocode_url = "https://maps.googleapis.com/maps/api/geocode/json"
params = {
    'address': 'Av. Ricardo Lyon 1841, Providencia, Santiago, Chile',
    'components': 'country:CL',
    'key': API_KEY
}

try:
    response = requests.get(geocode_url, params=params, timeout=10)
    data = response.json()

    print(f"  Status HTTP: {response.status_code}")
    print(f"  Status API: {data.get('status')}")

    if data.get('status') == 'OK':
        print("  [OK] Geocoding API funciona correctamente!")
        result = data['results'][0]
        print(f"  Dirección: {result.get('formatted_address')}")
        location = result['geometry']['location']
        print(f"  Coordenadas: {location['lat']}, {location['lng']}")
    elif data.get('status') == 'REQUEST_DENIED':
        print(f"  [X] ERROR: REQUEST_DENIED")
        print(f"  Mensaje: {data.get('error_message', 'Sin mensaje de error')}")
        print("\n  Posibles causas:")
        print("  1. La API 'Geocoding API' no está habilitada")
        print("  2. La API Key tiene restricciones que bloquean el uso")
        print("  3. Necesitas habilitar facturación (sin cargo dentro del límite gratuito)")
        print("\n  Soluciones:")
        print("  A. Ve a: https://console.cloud.google.com/apis/library/geocoding-backend.googleapis.com")
        print("     - Verifica que diga 'API habilitada' (no 'Habilitar')")
        print("  B. Ve a: https://console.cloud.google.com/apis/credentials")
        print("     - Haz clic en tu API Key")
        print("     - En 'API restrictions' debe estar en 'Don't restrict key' o incluir Geocoding API")
        print("  C. Ve a: https://console.cloud.google.com/billing")
        print("     - Puede que necesites vincular una cuenta de facturación")
        print("     - No te cobrarán dentro de los $200/mes gratuitos")
    else:
        print(f"  [X] ERROR: {data.get('status')}")
        print(f"  Mensaje: {data.get('error_message', 'Sin mensaje')}")

except Exception as e:
    print(f"  [X] ERROR de conexión: {str(e)}")

# 3. Probar Distance Matrix API
print("\n[3] Probando Distance Matrix API (HTTP directo)...")
distmatrix_url = "https://maps.googleapis.com/maps/api/distancematrix/json"
params = {
    'origins': '-33.4373,-70.5857',
    'destinations': '-33.4200,-70.6000',
    'mode': 'driving',
    'key': API_KEY
}

try:
    response = requests.get(distmatrix_url, params=params, timeout=10)
    data = response.json()

    print(f"  Status HTTP: {response.status_code}")
    print(f"  Status API: {data.get('status')}")

    if data.get('status') == 'OK':
        print("  [OK] Distance Matrix API funciona correctamente!")
        rows = data.get('rows', [])
        if rows:
            element = rows[0]['elements'][0]
            if element.get('status') == 'OK':
                distance = element['distance']['text']
                duration = element['duration']['text']
                print(f"  Distancia: {distance}")
                print(f"  Tiempo: {duration}")
    elif data.get('status') == 'REQUEST_DENIED':
        print(f"  [X] ERROR: REQUEST_DENIED")
        print(f"  Mensaje: {data.get('error_message', 'Sin mensaje de error')}")
        print("\n  Solución:")
        print("  Ve a: https://console.cloud.google.com/apis/library/distance-matrix-backend.googleapis.com")
        print("  - Verifica que la API esté habilitada")
    else:
        print(f"  [X] ERROR: {data.get('status')}")
        print(f"  Mensaje: {data.get('error_message', 'Sin mensaje')}")

except Exception as e:
    print(f"  [X] ERROR de conexión: {str(e)}")

# 4. Verificar restricciones de API Key
print("\n[4] Información importante:")
print("  - Para verificar el estado de tus APIs:")
print("    https://console.cloud.google.com/apis/dashboard")
print("  - Para verificar restricciones de tu API Key:")
print("    https://console.cloud.google.com/apis/credentials")
print("  - Para verificar facturación:")
print("    https://console.cloud.google.com/billing")

print("\n" + "="*70)
print(" FIN DEL DIAGNÓSTICO")
print("="*70)
