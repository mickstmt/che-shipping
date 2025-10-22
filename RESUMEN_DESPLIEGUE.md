# 📋 RESUMEN - Despliegue en Easypanel

## ✅ Archivos Preparados

Tu proyecto está listo para desplegar en Easypanel. Estos son los archivos clave:

### Archivos de Configuración Docker
- ✅ `Dockerfile` - Imagen Docker de la aplicación
- ✅ `.dockerignore` - Archivos a excluir de la imagen
- ✅ `gunicorn_config.py` - Configuración optimizada para Docker

### Archivos de Base de Datos
- ✅ `database/init.sql` - Script de inicialización de MySQL

### Archivos de Configuración
- ✅ `.env.example` - Plantilla de variables de entorno
- ✅ `.gitignore` - Evita subir archivos sensibles
- ✅ `requirements.txt` - Dependencias Python

### Documentación
- ✅ `README.md` - Documentación general
- ✅ `EASYPANEL_DEPLOYMENT.md` - Guía paso a paso para Easypanel
- ✅ `DEPLOYMENT.md` - Guía alternativa (VPS manual)

---

## 🚀 Pasos Rápidos para Desplegar

### 1. Subir a GitHub (5 min)

```powershell
cd C:\Users\Andree\Desktop\projects\flask\che-shipping

git init
git add .
git commit -m "Initial commit - Che Shipping para Easypanel"
git remote add origin https://github.com/TU-USUARIO/che-shipping.git
git branch -M main
git push -u origin main
```

### 2. En Easypanel - Crear MySQL (2 min)

1. Create Service → MySQL
2. Name: `shipping-mysql`
3. Database: `shipping_chile`
4. User: `shipping_user`
5. Password: (genera una segura)

### 3. En Easypanel - Crear App (3 min)

1. Create Service → App → From GitHub
2. Selecciona tu repositorio
3. Build Type: `Dockerfile`
4. Port: `8000`

### 4. Configurar Variables de Entorno (3 min)

```env
FLASK_ENV=production
SECRET_KEY=(genera con: python -c "import secrets; print(secrets.token_urlsafe(32))")
DB_HOST=shipping-mysql
DB_USER=shipping_user
DB_PASSWORD=(tu password de MySQL)
DB_NAME=shipping_chile
ROUTER_SERVICE_API_KEY=eyJvcmciOiI1YjNjZTM1OTc4NTExMTAwMDFjZjYyNDgiLCJpZCI6IjYwYTM2ZDg1MTA1YTRiM2U5MjFmZjdlM2RmZjlhMTkyIiwiaCI6Im11cm11cjY0In0=
DEFAULT_ORIGIN_ADDRESS=-33.43730244471958,-70.58568978400449
DEFAULT_ORIGIN_NAME=Amapolas 3959, Providencia, Santiago, Chile
```

### 5. Configurar Dominio (2 min)

1. En tu app → Domains
2. Add Domain: `envio.chetomi.cl`
3. Enable SSL ✅

### 6. Deploy! (2 min)

Click en **"Deploy"** y espera.

**Tiempo total: ~15-20 minutos**

---

## 🔗 URLs Finales

Después del despliegue:

- **Panel Admin**: `https://envio.chetomi.cl/shipping/`
- **API Quote**: `https://envio.chetomi.cl/shipping/api/quote`
- **API Jumpseller**: `https://envio.chetomi.cl/shipping/api/jumpseller/callback`
- **API Services**: `https://envio.chetomi.cl/shipping/api/jumpseller/services`

---

## 📝 Variables de Entorno Importantes

### Para generar SECRET_KEY segura:

```python
python -c "import secrets; print(secrets.token_urlsafe(32))"
```

### Coordenadas de Origen (tu tienda):

```
DEFAULT_ORIGIN_ADDRESS=-33.43730244471958,-70.58568978400449
DEFAULT_ORIGIN_NAME=Amapolas 3959, Providencia, Santiago, Chile
```

Estas coordenadas son **exactas** y evitan el problema de "Colegio Amapolas".

---

## ✅ Checklist Pre-Despliegue

Antes de subir a GitHub, verifica:

- [ ] `.env` NO está en el repositorio (está en `.gitignore`)
- [ ] `.env.example` NO contiene datos sensibles
- [ ] `Dockerfile` existe y está configurado
- [ ] `.dockerignore` existe
- [ ] `requirements.txt` tiene todas las dependencias
- [ ] Las coordenadas de origen son correctas

---

## 🐛 Troubleshooting Rápido

### No conecta a MySQL
→ Verifica que `DB_HOST=shipping-mysql` (nombre del servicio en Easypanel)

### Error 502
→ Revisa los logs en Easypanel → Logs tab

### App se reinicia
→ Verifica variables de entorno, especialmente `SECRET_KEY` y credenciales MySQL

---

## 📞 Configuración en Jumpseller

Una vez desplegado, ve a Jumpseller → Shipping → External Method:

**Callback URL:**
```
https://envio.chetomi.cl/shipping/api/jumpseller/callback
```

**Services URL:**
```
https://envio.chetomi.cl/shipping/api/jumpseller/services
```

---

## 🎉 ¡Todo Listo!

Para más detalles, consulta:
- [EASYPANEL_DEPLOYMENT.md](EASYPANEL_DEPLOYMENT.md) - Guía completa paso a paso
- [README.md](README.md) - Documentación del proyecto
