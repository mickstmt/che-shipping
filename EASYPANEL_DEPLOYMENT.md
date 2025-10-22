# 🚀 Despliegue en Easypanel

Guía paso a paso para desplegar **Che Shipping Service** en tu VPS usando Easypanel.

## Requisitos Previos

- ✅ VPS con Easypanel instalado
- ✅ Dominio apuntando a tu VPS (ej: `envio.chetomi.cl`)
- ✅ Código subido a GitHub
- ✅ Base de datos MySQL (puedes crearla en Easypanel)

---

## PASO 1: Preparar GitHub

### 1.1 Subir código a GitHub

```powershell
# En tu máquina local (Windows)
cd C:\Users\Andree\Desktop\projects\flask\che-shipping

# Inicializar git
git init

# Agregar archivos
git add .

# Commit inicial
git commit -m "Initial commit - Che Shipping con Easypanel"

# Conectar con GitHub (crea el repo primero en github.com)
git remote add origin https://github.com/TU-USUARIO/che-shipping.git

# Subir código
git branch -M main
git push -u origin main
```

---

## PASO 2: Crear Base de Datos MySQL en Easypanel

### 2.1 En Easypanel Dashboard

1. Click en **"Create Service"**
2. Selecciona **"MySQL"**
3. Configura:
   - **Name**: `shipping-mysql`
   - **Database Name**: `shipping_chile`
   - **Username**: `shipping_user`
   - **Password**: Genera una contraseña segura (guárdala)
4. Click **"Create"**
5. Espera a que inicie

### 2.2 Inicializar la base de datos

1. Click en tu servicio MySQL
2. Ve a la pestaña **"Console"** o **"Terminal"**
3. Ejecuta:

```bash
mysql -u mickstmt -p shipping_chile
```

4. Pega y ejecuta el contenido de `database/init.sql` (desde tu repo GitHub)

O alternativamente, puedes usar un cliente MySQL externo conectándote al puerto expuesto.

---

## PASO 3: Crear Aplicación Flask en Easypanel

### 3.1 Crear nueva App

1. En Easypanel, click **"Create Service"**
2. Selecciona **"App"**
3. Selecciona **"From GitHub"**

### 3.2 Configurar App

**General:**
- **Name**: `che-shipping`
- **Repository**: Selecciona tu repositorio `che-shipping`
- **Branch**: `main`
- **Build Path**: `/` (raíz)

**Build:**
- **Build Type**: `Dockerfile`
- **Dockerfile Path**: `Dockerfile`

**Deploy:**
- **Port**: `8000`
- **Health Check Path**: `/shipping/api/methods` (opcional)

### 3.3 Configurar Variables de Entorno

En la sección **Environment Variables**, agrega:

```env
# Flask
FLASK_ENV=production
ENVIRONMENT=production
SECRET_KEY=genera-una-clave-muy-segura-aqui-32-caracteres-minimo

# Base de datos MySQL
# Nota: Easypanel proporciona estas variables automáticamente si vinculas los servicios
DB_HOST=shipping-mysql  # O la IP interna que te da Easypanel
DB_USER=shipping_user
DB_PASSWORD=tu-password-mysql-segura
DB_NAME=shipping_chile

# RouterService API
ROUTER_SERVICE_API_KEY=eyJvcmciOiI1YjNjZTM1OTc4NTExMTAwMDFjZjYyNDgiLCJpZCI6IjYwYTM2ZDg1MTA1YTRiM2U5MjFmZjdlM2RmZjlhMTkyIiwiaCI6Im11cm11cjY0In0=

# Configuración de origen (coordenadas exactas)
DEFAULT_ORIGIN_ADDRESS=-33.43730244471958,-70.58568978400449
DEFAULT_ORIGIN_NAME=Amapolas 3959, Providencia, Santiago, Chile

# Gunicorn (opcional)
GUNICORN_WORKERS=4
LOG_LEVEL=info
```

**Importante para SECRET_KEY**: Genera una clave segura en Python:

```python
import secrets
print(secrets.token_urlsafe(32))
```

### 3.4 Vincular con MySQL

En Easypanel, puedes **vincular servicios**:

1. En la configuración de tu app `che-shipping`
2. Busca la sección **"Links"** o **"Dependencies"**
3. Agrega vínculo con `shipping-mysql`

Esto configura automáticamente la red interna de Docker para que tu app pueda conectarse a MySQL usando el nombre `shipping-mysql`.

---

## PASO 4: Configurar Dominio y SSL

### 4.1 Agregar Dominio

1. En la configuración de tu app
2. Ve a **"Domains"**
3. Click **"Add Domain"**
4. Ingresa: `envio.chetomi.cl`
5. Habilita **"Enable SSL"** (Let's Encrypt automático)

### 4.2 Verificar DNS

Asegúrate de que tu dominio apunta a la IP de tu VPS:

```bash
# Tipo A
envio.chetomi.cl  →  IP_DE_TU_VPS
```

---

## PASO 5: Desplegar

1. Click en **"Deploy"** o **"Build & Deploy"**
2. Easypanel:
   - Clonará tu repo de GitHub
   - Construirá la imagen Docker usando tu Dockerfile
   - Iniciará el contenedor
   - Configurará el proxy inverso con SSL

3. Monitorea los logs en tiempo real en la pestaña **"Logs"**

---

## PASO 6: Verificar Funcionamiento

### 6.1 Probar endpoints

```bash
# Verificar que responde
curl https://envio.chetomi.cl/shipping/api/methods

# Debería devolver JSON con los métodos de envío
```

### 6.2 Acceder al panel web

Abre en tu navegador:
```
https://envio.chetomi.cl/shipping/
```

### 6.3 Probar API de cotización

```bash
curl -X POST https://envio.chetomi.cl/shipping/api/quote \
  -H "Content-Type: application/json" \
  -d '{
    "origin": "",
    "destination": "Providencia, Santiago, Chile"
  }'
```

---

## 🔄 Actualizar la Aplicación

Cuando hagas cambios en tu código:

```bash
# En tu máquina local
git add .
git commit -m "Descripción de cambios"
git push origin main
```

En Easypanel:
1. Ve a tu app `che-shipping`
2. Click **"Rebuild"** o habilita **"Auto Deploy"** para que se actualice automáticamente con cada push

---

## 📊 Monitoreo en Easypanel

### Logs en tiempo real
1. Ve a tu app
2. Pestaña **"Logs"**
3. Verás los logs de Gunicorn en tiempo real

### Métricas
- **CPU Usage**
- **Memory Usage**
- **Network Traffic**

### Reiniciar la app
Si algo falla:
1. Click en **"Restart"**

---

## 🐛 Troubleshooting

### Error: Cannot connect to MySQL

**Solución:**
1. Verifica que el servicio MySQL esté corriendo
2. Verifica `DB_HOST` - debe ser el nombre del servicio MySQL en Easypanel
3. Verifica las credenciales en las variables de entorno

### Error: Module not found

**Solución:**
1. Verifica que `requirements.txt` esté en la raíz del repo
2. Verifica que el Dockerfile instale las dependencias
3. Rebuild la aplicación

### Error: 502 Bad Gateway

**Solución:**
1. Verifica los logs de la aplicación
2. Asegúrate de que Gunicorn está escuchando en `0.0.0.0:8000`
3. Verifica que el puerto configurado en Easypanel sea `8000`

### La app se reinicia constantemente

**Solución:**
1. Revisa los logs para ver el error
2. Probablemente un error en las variables de entorno
3. Verifica que la base de datos esté accesible

---

## 🔒 Seguridad

- ✅ Nunca subas `.env` a GitHub (ya está en `.gitignore`)
- ✅ Usa contraseñas fuertes para MySQL
- ✅ Cambia `SECRET_KEY` en producción
- ✅ SSL habilitado automáticamente por Easypanel
- ✅ Actualiza dependencias regularmente

---

## 📝 Variables de Entorno - Resumen

| Variable | Ejemplo | Descripción |
|----------|---------|-------------|
| `FLASK_ENV` | `production` | Ambiente de Flask |
| `SECRET_KEY` | `tu-clave-segura` | Clave secreta de Flask |
| `DB_HOST` | `shipping-mysql` | Host de MySQL (nombre del servicio) |
| `DB_USER` | `shipping_user` | Usuario de MySQL |
| `DB_PASSWORD` | `***` | Contraseña de MySQL |
| `DB_NAME` | `shipping_chile` | Nombre de la base de datos |
| `ROUTER_SERVICE_API_KEY` | `eyJ...` | API Key de OpenRouteService |
| `DEFAULT_ORIGIN_ADDRESS` | `-33.437,-70.586` | Coordenadas de origen |
| `DEFAULT_ORIGIN_NAME` | `Tu dirección` | Nombre legible del origen |

---

## ✅ Checklist Final

- [ ] Código subido a GitHub
- [ ] MySQL creado e inicializado en Easypanel
- [ ] App creada desde GitHub
- [ ] Variables de entorno configuradas
- [ ] Dominio configurado con SSL
- [ ] App desplegada exitosamente
- [ ] Endpoints funcionando
- [ ] Panel web accesible

---

## 🎉 ¡Listo!

Tu aplicación está desplegada en:
- **Panel Admin**: https://envio.chetomi.cl/shipping/
- **API Quote**: https://envio.chetomi.cl/shipping/api/quote
- **API Jumpseller**: https://envio.chetomi.cl/shipping/api/jumpseller/callback

Ahora puedes configurar este endpoint en Jumpseller para calcular tarifas de envío automáticamente.
