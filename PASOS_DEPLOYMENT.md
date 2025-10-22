# Pasos para Desplegar en VPS (Easypanel)

## Resumen: Qué vas a hacer

1. Subir código a GitHub
2. Crear base de datos MySQL en Easypanel
3. Crear aplicación Flask en Easypanel
4. Configurar variables de entorno
5. Desplegar y probar

---

## PASO 1: Subir a GitHub

### 1.1 Crear repositorio en GitHub
1. Ve a https://github.com/new
2. Nombre: `che-shipping`
3. Descripción: `Sistema de cotización de envíos para Chile`
4. **Público o Privado**: Tu elección
5. **NO marques** "Add README" ni ".gitignore" (ya los tenemos)
6. Click "Create repository"

### 1.2 Subir código desde tu PC

```powershell
# Abre PowerShell en la carpeta del proyecto
cd C:\Users\Andree\Desktop\projects\flask\che-shipping

# Verificar estado de git
git status

# Si no está inicializado, ejecuta:
git init

# Agregar todos los archivos
git add .

# Crear commit
git commit -m "Migración a Google Maps API - Listo para producción"

# Conectar con GitHub (reemplaza TU-USUARIO con tu username)
git remote add origin https://github.com/TU-USUARIO/che-shipping.git

# Subir código
git branch -M main
git push -u origin main
```

Si te pide credenciales, usa un **Personal Access Token** de GitHub (no tu contraseña).

---

## PASO 2: Crear Base de Datos en Easypanel

1. Abre Easypanel en tu navegador
2. Click **"Create Service"** → **"MySQL"**
3. Configura:
   - Name: `shipping-mysql`
   - Database: `shipping_chile`
   - User: `shipping_user`
   - Password: (Easypanel genera una, cópiala)
4. Click **"Create"**
5. Espera 1-2 minutos hasta que esté "Running"

### 2.1 Inicializar la base de datos

**Opción A - Desde Easypanel Console:**
1. Click en `shipping-mysql` → pestaña "Console"
2. Ejecuta:
   ```bash
   mysql -u shipping_user -p shipping_chile
   ```
3. Pega el contenido de `database/init.sql` (desde GitHub)

**Opción B - Desde tu PC con MySQL Client:**
1. Expón el puerto MySQL en Easypanel
2. Conecta desde tu PC:
   ```bash
   mysql -h TU_VPS_IP -P PUERTO -u shipping_user -p shipping_chile < database/init.sql
   ```

---

## PASO 3: Crear Aplicación Flask en Easypanel

1. En Easypanel, click **"Create Service"** → **"App"**
2. Selecciona **"From GitHub"**
3. Autoriza acceso a tu repositorio si es necesario
4. Configura:

### General
- **Name**: `che-shipping`
- **Repository**: Tu repositorio `che-shipping`
- **Branch**: `main`
- **Build Path**: `/`

### Build
- **Build Type**: `Dockerfile`
- **Dockerfile Path**: `Dockerfile`

### Deploy
- **Port**: `8000`
- **Health Check**: `/shipping/api/methods`

---

## PASO 4: Configurar Variables de Entorno

En la sección **Environment Variables** de Easypanel, agrega:

```env
FLASK_ENV=production
ENVIRONMENT=production
SECRET_KEY=usa-el-generador-abajo

DB_HOST=shipping-mysql
DB_USER=shipping_user
DB_PASSWORD=LA_PASSWORD_QUE_TE_DIO_EASYPANEL
DB_NAME=shipping_chile

GOOGLE_MAPS_API_KEY=AIzaSyD-mjIkJk_bep2RZ2griJnxfJ7UJEED3c8

DEFAULT_ORIGIN_ADDRESS=-33.43730244471958,-70.58568978400449
DEFAULT_ORIGIN_NAME=Amapolas 3959, Providencia, Santiago, Chile

GUNICORN_WORKERS=2
LOG_LEVEL=info
```

### Generar SECRET_KEY segura

Opción 1 - Online:
- Ve a: https://www.uuidgenerator.net/
- Copia cualquier UUID largo

Opción 2 - Python local:
```python
import secrets
print(secrets.token_urlsafe(32))
```

---

## PASO 5: Vincular Servicios (Opcional pero Recomendado)

1. En la configuración de `che-shipping`
2. Busca sección **"Links"** o **"Service Dependencies"**
3. Agrega vínculo con `shipping-mysql`

Esto permite que la app se conecte usando el nombre `shipping-mysql` en `DB_HOST`.

---

## PASO 6: Configurar Dominio

### 6.1 En tu proveedor de dominio

Crea registro DNS tipo **A**:
- **Host**: `envio` (o el subdominio que quieras)
- **Value**: IP de tu VPS
- **TTL**: 3600 o automático

### 6.2 En Easypanel

1. Ve a tu app `che-shipping`
2. Sección **"Domains"**
3. Click **"Add Domain"**
4. Ingresa: `envio.chetomi.cl`
5. Habilita **SSL/HTTPS** (Easypanel usa Let's Encrypt automáticamente)
6. Click **"Save"**

---

## PASO 7: Desplegar

1. Click **"Deploy"** en Easypanel
2. Espera 3-5 minutos (primera vez tarda más)
3. Monitorea logs en la pestaña **"Logs"**

### Verificar que funciona

Una vez desplegado, abre:

1. **Health check**: https://envio.chetomi.cl/shipping/api/methods
   - Debería mostrar JSON con métodos de envío

2. **Panel admin**: https://envio.chetomi.cl/shipping/
   - Debería cargar la interfaz

3. **Probar cotización**: Ingresa dirección de prueba
   - Ejemplo: `Av. Ricardo Lyon 1841, Providencia, Santiago`
   - Debería mostrar opciones de envío

---

## PASO 8: Configurar Jumpseller (Webhook)

### URL del webhook para Jumpseller:

```
https://envio.chetomi.cl/shipping/api/jumpseller
```

### Configuración en Jumpseller:

1. Ve a Jumpseller → Configuración → Envíos
2. Selecciona **"Método Externo"**
3. Pega la URL del webhook
4. Selecciona método: **POST**
5. Headers (si es necesario):
   ```
   Content-Type: application/json
   ```
6. Guarda

---

## Troubleshooting

### Error: Can't connect to MySQL
- Verifica que `DB_HOST=shipping-mysql` esté correcto
- Verifica que los servicios estén vinculados
- Revisa logs de MySQL en Easypanel

### Error: Google Maps API
- Verifica que la API Key sea correcta
- Verifica que no tenga restricciones de IP/dominio
- Asegúrate que Geocoding API y Distance Matrix API estén habilitadas

### Error 500 en la web
- Revisa logs en Easypanel → pestaña "Logs"
- Busca el error específico
- Verifica todas las variables de entorno

### La app no inicia
- Verifica que el Dockerfile esté correcto
- Revisa logs de build en Easypanel
- Asegúrate que el puerto sea 8000

---

## Monitoreo Post-Deployment

### Verificar uso de Google Maps API

1. Ve a: https://console.cloud.google.com/apis/dashboard
2. Selecciona tu proyecto
3. Ve a "Geocoding API" → Métricas
4. Monitorea requests diarios
5. Con el límite gratuito ($200/mes) tienes ~40,000 geocoding requests

### Logs de la aplicación

En Easypanel:
- Click en `che-shipping` → Pestaña "Logs"
- Filtra por "ERROR" para ver errores
- Filtra por "INFO" para ver requests normales

---

## Resumen de URLs

Una vez desplegado, tendrás:

- **Panel Admin**: https://envio.chetomi.cl/shipping/
- **API Quote**: https://envio.chetomi.cl/shipping/api/quote
- **Webhook Jumpseller**: https://envio.chetomi.cl/shipping/api/jumpseller
- **Health Check**: https://envio.chetomi.cl/shipping/api/methods

---

## Archivos Importantes en el Repo

- `Dockerfile` - Configuración de contenedor
- `docker-compose.yml` - Para pruebas locales
- `gunicorn_config.py` - Configuración del servidor
- `requirements.txt` - Dependencias Python
- `.env.example` - Template de variables de entorno
- `database/init.sql` - Script de inicialización de DB
- `EASYPANEL_DEPLOYMENT.md` - Guía detallada
- `test_google_maps.py` - Script de pruebas (puedes ejecutarlo en producción)
- `diagnostico_google_api.py` - Diagnóstico de Google API

---

¡Listo! Ahora tu aplicación debería estar funcionando en producción.
