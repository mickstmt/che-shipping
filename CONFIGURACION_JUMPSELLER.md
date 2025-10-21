# Configuración de Envíos Externos en Jumpseller

## Información General

Este documento explica cómo configurar dos métodos de envío externos en Jumpseller para integrar con tu sistema de envíos.

**URL del Servicio en Producción:** `https://envio.chetomi.cl`

---

## Paso 1: Acceder a Configuración de Envíos

1. Ingresa a tu panel de Jumpseller
2. Ve a **Configuración → Envíos**
3. Haz clic en **"Agregar Método de Envío Externo"**

---

## Configuración 1: Envío Hoy

### Datos del Formulario

| Campo | Valor |
|-------|-------|
| **Nombre del método*** | `Envío Hoy` |
| **URL de devolución de llamada** | (dejar vacío) |
| **URL para buscar la lista de servicios disponibles*** | `https://envio.chetomi.cl/shipping/api/quote` |
| **Token de API** | (dejar vacío - no requiere autenticación) |

### Características

- **Disponibilidad:** Lunes a Domingo, de 00:01 a 18:00 hrs
- **Cobertura:** Hasta 7 km desde Santiago Centro
- **Descripción:** Entrega el mismo día para pedidos realizados antes de las 18:00 hrs

### JSON de Request que Jumpseller enviará:

```json
{
  "destination": "Dirección completa del cliente",
  "origin": "Santiago Centro, Chile",
  "session_id": "jumpseller_session_id"
}
```

### JSON de Response esperado:

```json
{
  "success": true,
  "route": {
    "distance_km": 3.2,
    "duration_minutes": 18
  },
  "shipping_options": [
    {
      "method_code": "envio_hoy",
      "method_name": "Envío Hoy",
      "price_clp": 3500,
      "available_until": "18:00",
      "description": "Entrega el mismo día (disponible hasta las 18:00)"
    }
  ]
}
```

---

## Configuración 2: Envío Programado

### Datos del Formulario

| Campo | Valor |
|-------|-------|
| **Nombre del método*** | `Envío Programado` |
| **URL de devolución de llamada** | (dejar vacío) |
| **URL para buscar la lista de servicios disponibles*** | `https://envio.chetomi.cl/shipping/api/quote` |
| **Token de API** | (dejar vacío - no requiere autenticación) |

### Características

- **Disponibilidad:** 24/7 (siempre disponible)
- **Cobertura:** Hasta 7 km desde Santiago Centro
- **Descripción:** Entrega programada para el día siguiente

### JSON de Request que Jumpseller enviará:

```json
{
  "destination": "Dirección completa del cliente",
  "origin": "Santiago Centro, Chile",
  "session_id": "jumpseller_session_id"
}
```

### JSON de Response esperado:

```json
{
  "success": true,
  "route": {
    "distance_km": 4.5,
    "duration_minutes": 25
  },
  "shipping_options": [
    {
      "method_code": "envio_programado",
      "method_name": "Envío Programado",
      "price_clp": 4500,
      "available_until": "23:59",
      "description": "Entrega programada para el día siguiente"
    }
  ]
}
```

---

## Tarifas por Distancia

Las tarifas se calculan automáticamente según la distancia desde Santiago Centro:

| Distancia (km) | Tarifa (CLP) |
|----------------|--------------|
| 0 - 3 km       | $3.500       |
| 3 - 4 km       | $4.500       |
| 4 - 5 km       | $5.000       |
| 5 - 6 km       | $5.500       |
| 6 - 7 km       | $6.500       |

---

## Endpoints Disponibles

### 1. Cotizar Envío (Principal para Jumpseller)

**Endpoint:** `POST https://envio.chetomi.cl/shipping/api/quote`

**Headers:**
```
Content-Type: application/json
```

**Body:**
```json
{
  "destination": "Providencia, Santiago, Chile",
  "origin": "Santiago Centro, Chile",
  "session_id": "optional_id"
}
```

**Response (Success):**
```json
{
  "success": true,
  "origin": {
    "address": "Santiago Centro, Chile",
    "formatted_address": "Santiago Centro, Región Metropolitana, Chile",
    "lat": -33.4489,
    "lng": -70.6693
  },
  "destination": {
    "address": "Providencia, Santiago, Chile",
    "formatted_address": "Providencia, Región Metropolitana, Chile",
    "lat": -33.4266,
    "lng": -70.6104
  },
  "route": {
    "distance_km": 3.2,
    "duration_minutes": 18
  },
  "shipping_options": [
    {
      "method_code": "envio_hoy",
      "method_name": "Envío Hoy",
      "description": "Entrega el mismo día (disponible hasta las 18:00)",
      "price_clp": 3500,
      "price_formatted": "$3,500",
      "distance_km": 3.2,
      "duration_minutes": 18,
      "available_until": "18:00",
      "zone_range": "3.0-4.0 km"
    },
    {
      "method_code": "envio_programado",
      "method_name": "Envío Programado",
      "description": "Entrega programada para el día siguiente",
      "price_clp": 3500,
      "price_formatted": "$3,500",
      "distance_km": 3.2,
      "duration_minutes": 18,
      "available_until": "23:59",
      "zone_range": "3.0-4.0 km"
    }
  ],
  "session_id": "optional_id",
  "quote_count": 2
}
```

**Response (Error - Fuera de cobertura):**
```json
{
  "success": false,
  "error": "No hay métodos de envío disponibles para 8.5 km",
  "distance_km": 8.5,
  "max_distance": 7.0,
  "available_zones": [
    "0.0-3.0km",
    "3.0-4.0km",
    "4.0-5.0km",
    "5.0-6.0km",
    "6.0-7.0km"
  ]
}
```

**Response (Error - Dirección no encontrada):**
```json
{
  "success": false,
  "error": "No se pudo encontrar la dirección de destino",
  "status": "GEOCODING_FAILED"
}
```

---

### 2. Listar Métodos de Envío

**Endpoint:** `GET https://envio.chetomi.cl/shipping/api/methods`

**Response:**
```json
{
  "success": true,
  "methods": [
    {
      "id": 1,
      "name": "Envío Hoy",
      "code": "envio_hoy",
      "description": "Entrega el mismo día (disponible hasta las 18:00)",
      "is_active": true,
      "start_time": "00:01",
      "end_time": "18:00",
      "max_km": 7.0,
      "is_available_now": true
    },
    {
      "id": 2,
      "name": "Envío Programado",
      "code": "envio_programado",
      "description": "Entrega programada para el día siguiente",
      "is_active": true,
      "start_time": "00:00",
      "end_time": "23:59",
      "max_km": 7.0,
      "is_available_now": true
    }
  ],
  "count": 2
}
```

---

### 3. Listar Zonas y Tarifas

**Endpoint:** `GET https://envio.chetomi.cl/shipping/api/zones`

**Response:**
```json
{
  "success": true,
  "zones": [
    {
      "id": 1,
      "min_km": 0.0,
      "max_km": 3.0,
      "price_clp": 3500,
      "price_formatted": "$3,500",
      "range_text": "0.0-3.0 km",
      "is_active": true
    },
    {
      "id": 2,
      "min_km": 3.0,
      "max_km": 4.0,
      "price_clp": 4500,
      "price_formatted": "$4,500",
      "range_text": "3.0-4.0 km",
      "is_active": true
    }
  ],
  "count": 5
}
```

---

## Notas Importantes

### Diferencias entre los dos métodos:

1. **Envío Hoy:**
   - Solo disponible de 00:01 a 18:00 hrs
   - Si un cliente hace un pedido después de las 18:00, NO aparecerá como opción
   - Entrega el mismo día

2. **Envío Programado:**
   - Disponible 24/7
   - Siempre disponible independiente de la hora
   - Entrega al día siguiente

### ¿Por qué configurar ambos si usan la misma URL?

- **La misma URL API retorna ambos métodos** en `shipping_options`
- Jumpseller filtrará automáticamente según la disponibilidad horaria
- El sistema detecta la hora actual y solo retorna los métodos disponibles
- Configurar ambos en Jumpseller te permite tener control individual de cada uno

### Validaciones del Sistema:

1. **Distancia:** Máximo 7 km desde Santiago Centro
2. **Horario:** "Envío Hoy" solo hasta las 18:00
3. **Geocodificación:** Debe poder encontrar la dirección en Chile
4. **Zona:** Debe existir una tarifa para la distancia calculada

---

## Testing

### Probar desde el Panel Web

1. Abre: `https://envio.chetomi.cl/shipping/`
2. Usa el "Probador de API" en la parte inferior
3. Ingresa direcciones de ejemplo:
   - Providencia, Santiago, Chile
   - Las Condes, Santiago, Chile
   - Ñuñoa, Santiago, Chile

### Probar con cURL

```bash
curl -X POST https://envio.chetomi.cl/shipping/api/quote \
  -H "Content-Type: application/json" \
  -d '{
    "destination": "Providencia, Santiago, Chile",
    "origin": "Santiago Centro, Chile",
    "session_id": "test_123"
  }'
```

---

## Soporte

Si tienes problemas con la integración:

1. Verifica que el servidor esté corriendo en `https://envio.chetomi.cl`
2. Revisa los logs del servidor
3. Prueba el endpoint directamente desde el navegador o Postman
4. Verifica que la base de datos tenga datos inicializados

---

## Resumen de URLs para Jumpseller

Ambos métodos de envío usan la misma URL:

```
https://envio.chetomi.cl/shipping/api/quote
```

El sistema automáticamente:
- Calcula la distancia usando RouterService
- Determina qué métodos están disponibles según el horario
- Aplica la tarifa según la distancia
- Retorna solo las opciones válidas para ese momento
