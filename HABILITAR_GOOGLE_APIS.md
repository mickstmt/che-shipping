# Guía: Habilitar Google Maps APIs

## Problema Actual

Error: `REQUEST_DENIED - This API project is not authorized to use this API`

**Causa**: Las APIs específicas no están habilitadas en tu proyecto de Google Cloud.

## Solución: Habilitar las 3 APIs Requeridas

### Paso 1: Ir a Google Cloud Console

1. Abre tu navegador
2. Ve a: https://console.cloud.google.com/
3. Asegúrate de estar en el proyecto correcto (donde creaste la API Key)

### Paso 2: Habilitar Geocoding API

1. Ve a: https://console.cloud.google.com/apis/library/geocoding-backend.googleapis.com
2. Haz clic en el botón **"HABILITAR"** o **"ENABLE"**
3. Espera unos segundos hasta que se active

### Paso 3: Habilitar Distance Matrix API

1. Ve a: https://console.cloud.google.com/apis/library/distance-matrix-backend.googleapis.com
2. Haz clic en el botón **"HABILITAR"** o **"ENABLE"**
3. Espera unos segundos hasta que se active

### Paso 4: Habilitar Places API (Opcional pero recomendado)

1. Ve a: https://console.cloud.google.com/apis/library/places-backend.googleapis.com
2. Haz clic en el botón **"HABILITAR"** o **"ENABLE"**
3. Espera unos segundos hasta que se active

## Método Alternativo (Búsqueda Manual)

Si los enlaces anteriores no funcionan:

1. Ve a: https://console.cloud.google.com/apis/library
2. En el buscador, escribe: **"Geocoding API"**
3. Haz clic en el resultado y presiona **"HABILITAR"**
4. Repite para **"Distance Matrix API"**
5. Repite para **"Places API"** (opcional)

## Verificar que las APIs están Habilitadas

1. Ve a: https://console.cloud.google.com/apis/dashboard
2. Deberías ver las siguientes APIs en la lista:
   - ✓ Geocoding API
   - ✓ Distance Matrix API
   - ✓ Places API (opcional)

## Después de Habilitar las APIs

1. Espera 1-2 minutos para que los cambios se propaguen
2. Ejecuta nuevamente el script de pruebas:
   ```bash
   python test_google_maps.py
   ```

## Costos y Límites

Con el plan gratuito de Google Maps ($200 USD/mes de crédito):

- **Geocoding API**: $5 por 1,000 requests → 40,000 requests gratis/mes
- **Distance Matrix API**: $5 por 1,000 elements → 40,000 elements gratis/mes
- **Total**: ~20,000 cotizaciones completas gratis/mes (con caché activo)

**No necesitas tarjeta de crédito** para el nivel gratuito básico, pero para habilitar las APIs puede que te la pidan (no te cobrarán a menos que excedas el límite).

## Restricciones de API Key (Recomendado para Producción)

Una vez que todo funcione, puedes restringir tu API Key:

1. Ve a: https://console.cloud.google.com/apis/credentials
2. Haz clic en tu API Key
3. En "API restrictions" → Selecciona "Restrict key"
4. Marca solo:
   - Geocoding API
   - Distance Matrix API
   - Places API

Esto evita que alguien use tu API Key para otros servicios.

## Notas Importantes

- Las APIs se habilitan **por proyecto**, no por API Key
- Puede tardar hasta 5 minutos en propagarse
- Si sigues teniendo problemas, verifica que la API Key pertenezca al proyecto correcto
- Para verificar qué proyecto usa tu API Key: https://console.cloud.google.com/apis/credentials
