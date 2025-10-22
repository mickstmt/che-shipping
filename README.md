# Che Shipping - Sistema de Cotización de Envíos

Sistema de cotización de envíos para Chile integrado con Jumpseller, usando OpenRouteService para cálculo de rutas.

## 🚀 Características

- ✅ Cálculo de distancias y tiempos usando OpenRouteService
- ✅ Zonas de envío configurables por kilómetros
- ✅ Múltiples métodos de envío con horarios
- ✅ API REST para integración con Jumpseller
- ✅ Panel de administración web
- ✅ Historial de cotizaciones

## 📋 Requisitos

- Python 3.9+
- MySQL 8.0+
- Nginx (para producción)

## 🛠️ Instalación Local

```bash
# Clonar repositorio
git clone https://github.com/tu-usuario/che-shipping.git
cd che-shipping

# Crear entorno virtual
python -m venv venv
source venv/bin/activate  # En Windows: venv\Scripts\activate

# Instalar dependencias
pip install -r requirements.txt

# Configurar variables de entorno
cp .env.example .env
# Editar .env con tus valores

# Inicializar base de datos
mysql -u root -p < database/init.sql

# Ejecutar aplicación
python run.py
```

## 🌐 Despliegue en Producción

### Opción 1: Easypanel (Recomendado - Más Fácil)
Ver [EASYPANEL_DEPLOYMENT.md](EASYPANEL_DEPLOYMENT.md) para despliegue con Docker en Easypanel.

### Opción 2: VPS Manual
Ver [DEPLOYMENT.md](DEPLOYMENT.md) para instalación manual con Nginx + Gunicorn.

## 📚 API Endpoints

### Para Jumpseller

**POST** `/shipping/api/jumpseller/callback`
```json
{
  "request": {
    "from": { "address": "...", "city": "..." },
    "to": { "address": "...", "city": "..." },
    "cart_id": "123"
  }
}
```

**GET** `/shipping/api/jumpseller/services`

### Para Testing

**POST** `/shipping/api/quote`
```json
{
  "origin": "Santiago Centro, Chile",
  "destination": "Providencia, Santiago, Chile"
}
```

## 🔧 Configuración

### Variables de Entorno

- `FLASK_ENV`: development | production
- `DB_HOST`: Host de MySQL
- `DB_USER`: Usuario de MySQL
- `DB_PASSWORD`: Contraseña de MySQL
- `DB_NAME`: Nombre de base de datos
- `ROUTER_SERVICE_API_KEY`: API Key de OpenRouteService
- `DEFAULT_ORIGIN_ADDRESS`: Coordenadas de origen (lat,lng)
- `DEFAULT_ORIGIN_NAME`: Nombre legible del origen

### Zonas de Envío

Las zonas se configuran en la tabla `shipping_zones`:

| Rango (km) | Precio (CLP) |
|------------|--------------|
| 0-3        | $3,500       |
| 3-4        | $4,500       |
| 4-5        | $5,000       |
| 5-6        | $5,500       |
| 6-8        | $6,500       |

## 📝 Licencia

MIT License - ver LICENSE para más detalles

## 👤 Autor

Che Shipping Team
