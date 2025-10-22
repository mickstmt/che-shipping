#!/usr/bin/env python3
"""
Script de pruebas para validar la integración con Google Maps APIs
Prueba diferentes tipos de direcciones y niveles de precisión
"""

import os
import sys
from dotenv import load_dotenv

# Cargar variables de entorno
load_dotenv()

# Verificar que existe GOOGLE_MAPS_API_KEY
if not os.environ.get('GOOGLE_MAPS_API_KEY') or os.environ.get('GOOGLE_MAPS_API_KEY') == 'tu_google_maps_api_key_aqui':
    print("ERROR: GOOGLE_MAPS_API_KEY no está configurada en .env")
    print("\nPor favor:")
    print("1. Abre el archivo .env")
    print("2. Reemplaza 'tu_google_maps_api_key_aqui' con tu API Key real de Google Maps")
    print("3. Vuelve a ejecutar este script")
    sys.exit(1)

# Importar el servicio
from app.services.router_service import router_service

def print_separator(title=""):
    print("\n" + "="*70)
    if title:
        print(f" {title}")
        print("="*70)
    else:
        print()

def test_address(description, address, expected_level=None):
    """Probar validación de una dirección"""
    print(f"\n[TEST] {description}")
    print(f"Dirección: {address}")
    print("-" * 70)

    try:
        result = router_service.get_distance_and_time("", address)

        if result['success']:
            print(f"[OK] Validación exitosa")
            print(f"  Dirección formateada: {result['destination']['formatted_address']}")
            print(f"  Coordenadas: {result['destination']['lat']}, {result['destination']['lng']}")
            print(f"  Distancia: {result['route']['distance_km']} km ({result['route']['distance_text']})")
            print(f"  Tiempo: {result['route']['duration_minutes']} min ({result['route']['duration_text']})")

            validation = result['destination']['validation']
            print(f"\n  Validación:")
            print(f"    Nivel: {validation['level']}")
            print(f"    Granularidad: {validation['granularity']}")
            print(f"    Confianza: {validation['confidence']}")

            if validation.get('warning'):
                print(f"    [!] Warning: {validation['warning']}")

            if 'warning' in result:
                print(f"\n  [!] ADVERTENCIA GENERAL: {result['warning']}")

            if expected_level and validation['level'] != expected_level:
                print(f"  [!] NOTA: Se esperaba nivel '{expected_level}' pero se obtuvo '{validation['level']}'")

            return True
        else:
            print(f"[FAIL] Error: {result.get('error')}")
            print(f"  Status: {result.get('status')}")
            if 'destination_validation' in result:
                val = result['destination_validation']
                print(f"  Granularidad: {val.get('granularity')}")
                print(f"  Nivel: {val.get('validation_level')}")
            return False

    except Exception as e:
        print(f"[ERROR] Excepción: {str(e)}")
        import traceback
        traceback.print_exc()
        return False

def test_cache():
    """Probar funcionamiento del caché"""
    print_separator("TEST DE CACHÉ")

    address = "Av. Ricardo Lyon 1841, Providencia, Santiago, Chile"

    print("\n[1] Primera llamada (sin caché)...")
    result1 = router_service.get_distance_and_time("", address)

    print("\n[2] Segunda llamada (debería usar caché)...")
    result2 = router_service.get_distance_and_time("", address)

    print("\n[3] Estadísticas del caché:")
    stats = router_service.get_cache_stats()
    print(f"  Total de entradas: {stats['total_entries']}")
    for entry in stats['entries']:
        print(f"    - {entry['address']}: {entry['age_minutes']} minutos de antigüedad")

    if result1['success'] and result2['success']:
        print("\n[OK] Caché funcionando correctamente")
        return True
    else:
        print("\n[FAIL] Caché no funcionó correctamente")
        return False

def main():
    """Ejecutar todas las pruebas"""
    print_separator("PRUEBAS DE GOOGLE MAPS API - CHE SHIPPING")
    print("\nVerificando configuración...")
    print(f"  API Key configurada: Sí (primeros 20 chars: {os.environ.get('GOOGLE_MAPS_API_KEY')[:20]}...)")
    print(f"  Origen por defecto: {os.environ.get('DEFAULT_ORIGIN_NAME')}")
    print(f"  Coordenadas origen: {os.environ.get('DEFAULT_ORIGIN_ADDRESS')}")

    # Test 1: Dirección muy precisa (debería ser ACCEPT)
    print_separator("TEST 1: Dirección Precisa con Número")
    test_address(
        "Dirección completa con número de casa",
        "Av. Ricardo Lyon 1841, Providencia, Santiago, Chile",
        expected_level='accept'
    )

    # Test 2: Dirección sin número (debería ser WARNING o ACCEPT dependiendo del resultado)
    print_separator("TEST 2: Dirección sin Número")
    test_address(
        "Avenida sin número específico",
        "Av. Providencia, Providencia, Santiago, Chile",
        expected_level='warning'
    )

    # Test 3: Solo comuna (debería ser REJECT)
    print_separator("TEST 3: Solo Comuna (debería rechazarse)")
    test_address(
        "Solo nombre de comuna",
        "Providencia, Santiago, Chile",
        expected_level='reject'
    )

    # Test 4: Dirección completa de tienda común
    print_separator("TEST 4: Dirección Completa Típica")
    test_address(
        "Dirección típica de tienda",
        "Av. Apoquindo 4501, Las Condes, Santiago, Chile",
        expected_level='accept'
    )

    # Test 5: Dirección de otra región
    print_separator("TEST 5: Dirección en Otra Región")
    test_address(
        "Dirección en Valparaíso",
        "Av. España 1234, Valparaíso, Chile",
        expected_level='accept'
    )

    # Test 6: Dirección muy lejana
    print_separator("TEST 6: Dirección Muy Lejana")
    test_address(
        "Dirección en región lejana (debería exceder zonas)",
        "Av. Arturo Prat 500, Iquique, Chile",
        expected_level='accept'
    )

    # Test 7: Prueba de caché
    test_cache()

    # Resumen final
    print_separator("PRUEBAS COMPLETADAS")
    print("\n[OK] Todas las pruebas básicas han sido ejecutadas")
    print("\nRecomendaciones:")
    print("  1. Verifica que las direcciones precisas sean aceptadas")
    print("  2. Verifica que las direcciones sin número muestren advertencia")
    print("  3. Verifica que las direcciones muy imprecisas sean rechazadas")
    print("  4. Revisa los logs para confirmar que el caché está funcionando")
    print("\nPara producción:")
    print("  - Monitorea el uso de la API en Google Cloud Console")
    print("  - El caché reduce llamadas API para direcciones repetidas")
    print("  - Límite gratuito: ~$200/mes = ~16,000 requests")
    print_separator()

if __name__ == '__main__':
    try:
        main()
    except KeyboardInterrupt:
        print("\n\n[!] Pruebas interrumpidas por el usuario")
        sys.exit(0)
    except Exception as e:
        print(f"\n\n[ERROR CRÍTICO] {str(e)}")
        import traceback
        traceback.print_exc()
        sys.exit(1)
