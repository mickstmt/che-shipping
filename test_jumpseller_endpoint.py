#!/usr/bin/env python3
"""
Script para probar el endpoint de Jumpseller
Simula una petición real de Jumpseller
"""

import requests
import json

# URL del endpoint (cambiar según ambiente)
BASE_URL = "http://localhost:5000"  # Local
# BASE_URL = "https://envio.chetomi.cl"  # Producción

def test_jumpseller_callback():
    """Probar endpoint de callback con datos simulados de Jumpseller"""

    url = f"{BASE_URL}/shipping/api/jumpseller/callback"

    # Payload simulando estructura de Jumpseller
    payload = {
        "request": {
            "cart_id": "test-cart-123",
            "order_id": "",
            "to": {
                "address": "Av. Ricardo Lyon",
                "street_number": "1841",
                "city": "Providencia",
                "region_name": "Región Metropolitana",
                "municipality_name": "Providencia",
                "country": "Chile"
            },
            "from": {
                "address": "Amapolas 3959",
                "city": "Providencia",
                "region_name": "Región Metropolitana"
            }
        }
    }

    print("="*70)
    print("TEST: Jumpseller Callback Endpoint")
    print("="*70)
    print(f"\nURL: {url}")
    print(f"\nPayload enviado:")
    print(json.dumps(payload, indent=2))
    print("\n" + "-"*70)

    try:
        response = requests.post(url, json=payload, timeout=30)

        print(f"\nStatus Code: {response.status_code}")
        print(f"\nRespuesta:")
        print(json.dumps(response.json(), indent=2))

        if response.status_code == 200:
            data = response.json()
            if data.get('rates') and len(data['rates']) > 0:
                print("\n[OK] Endpoint funcionando correctamente!")
                print(f"Se encontraron {len(data['rates'])} opciones de envío")
                for rate in data['rates']:
                    print(f"  - {rate['service_name']}: ${rate['total_price']} CLP")
            else:
                print("\n[WARNING] No se encontraron rates disponibles")
                if 'error' in data:
                    print(f"Error: {data['error']}")
        else:
            print(f"\n[ERROR] Endpoint retornó código {response.status_code}")

    except requests.exceptions.ConnectionError:
        print("\n[ERROR] No se pudo conectar al servidor")
        print("Asegúrate que Flask esté corriendo en el puerto correcto")
    except Exception as e:
        print(f"\n[ERROR] {str(e)}")

def test_jumpseller_services():
    """Probar endpoint de listado de servicios"""

    url = f"{BASE_URL}/shipping/api/jumpseller/services"

    print("\n" + "="*70)
    print("TEST: Jumpseller Services Endpoint")
    print("="*70)
    print(f"\nURL: {url}")
    print("\n" + "-"*70)

    try:
        response = requests.get(url, timeout=10)

        print(f"\nStatus Code: {response.status_code}")
        print(f"\nRespuesta:")
        print(json.dumps(response.json(), indent=2))

        if response.status_code == 200:
            data = response.json()
            if data.get('services'):
                print(f"\n[OK] Se encontraron {len(data['services'])} servicios")
                for service in data['services']:
                    print(f"  - {service['service_name']} ({service['service_code']})")
            else:
                print("\n[WARNING] No hay servicios disponibles")
        else:
            print(f"\n[ERROR] Endpoint retornó código {response.status_code}")

    except requests.exceptions.ConnectionError:
        print("\n[ERROR] No se pudo conectar al servidor")
    except Exception as e:
        print(f"\n[ERROR] {str(e)}")

if __name__ == '__main__':
    print("\nPRUEBAS DE ENDPOINTS JUMPSELLER\n")

    # Probar endpoint de servicios
    test_jumpseller_services()

    # Probar endpoint de callback
    test_jumpseller_callback()

    print("\n" + "="*70)
    print("PRUEBAS COMPLETADAS")
    print("="*70)
    print("\nSi ambos tests pasaron, las URLs están correctas para Jumpseller:")
    print("  - Callback: /shipping/api/jumpseller/callback")
    print("  - Services: /shipping/api/jumpseller/services")
    print("\n")
