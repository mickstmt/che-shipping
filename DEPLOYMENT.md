# 🚀 Guía de Despliegue en VPS

## Requisitos del VPS

- Ubuntu 20.04+ / Debian 11+
- 1GB RAM mínimo (2GB recomendado)
- 10GB espacio en disco
- Acceso root o sudo

## FASE 1: Preparar GitHub

### 1. Crear repositorio en GitHub

```bash
# En tu máquina local (Windows)
cd C:\Users\Andree\Desktop\projects\flask\che-shipping

# Inicializar git si no está
git init

# Agregar archivos
git add .

# Primer commit
git commit -m "Initial commit - Che Shipping Service"

# Agregar repositorio remoto (reemplaza con tu URL)
git remote add origin https://github.com/TU-USUARIO/che-shipping.git

# Subir código
git branch -M main
git push -u origin main
```

## FASE 2: Configurar el VPS

### 2. Conectar al VPS

```bash
ssh usuario@tu-vps-ip
```

### 3. Actualizar sistema

```bash
sudo apt update
sudo apt upgrade -y
```

### 4. Instalar dependencias del sistema

```bash
# Python y herramientas
sudo apt install -y python3 python3-pip python3-venv

# MySQL
sudo apt install -y mysql-server

# Nginx
sudo apt install -y nginx

# Git
sudo apt install -y git

# Certbot para SSL
sudo apt install -y certbot python3-certbot-nginx
```

### 5. Configurar MySQL

```bash
# Iniciar MySQL
sudo systemctl start mysql
sudo systemctl enable mysql

# Configurar seguridad
sudo mysql_secure_installation

# Crear base de datos y usuario
sudo mysql
```

```sql
CREATE DATABASE shipping_chile CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;
CREATE USER 'shipping_user'@'localhost' IDENTIFIED BY 'TU_PASSWORD_SEGURA';
GRANT ALL PRIVILEGES ON shipping_chile.* TO 'shipping_user'@'localhost';
FLUSH PRIVILEGES;
EXIT;
```

### 6. Clonar el repositorio

```bash
# Crear directorio
sudo mkdir -p /var/www
cd /var/www

# Clonar (reemplaza con tu URL)
sudo git clone https://github.com/TU-USUARIO/che-shipping.git
cd che-shipping

# Cambiar permisos
sudo chown -R www-data:www-data /var/www/che-shipping
```

### 7. Configurar entorno Python

```bash
# Crear entorno virtual
sudo -u www-data python3 -m venv venv

# Activar entorno
source venv/bin/activate

# Instalar dependencias
pip install -r requirements.txt

# Desactivar entorno
deactivate
```

### 8. Configurar variables de entorno

```bash
# Copiar plantilla
sudo cp .env.example .env

# Editar con tus valores
sudo nano .env
```

Configurar:
```env
FLASK_ENV=production
ENVIRONMENT=production
SECRET_KEY=tu-clave-secreta-muy-segura-generada-aleatoriamente
DB_HOST=localhost
DB_USER=shipping_user
DB_PASSWORD=TU_PASSWORD_SEGURA
DB_NAME=shipping_chile
ROUTER_SERVICE_API_KEY=tu_api_key
DEFAULT_ORIGIN_ADDRESS=-33.43730244471958,-70.58568978400449
DEFAULT_ORIGIN_NAME=Amapolas 3959, Providencia, Santiago, Chile
```

### 9. Inicializar base de datos

```bash
# Activar entorno
source venv/bin/activate

# Ejecutar desde Python
python
```

```python
from app import create_app, db
app = create_app()
with app.app_context():
    db.create_all()
    print("Base de datos creada exitosamente")
exit()
```

### 10. Configurar Gunicorn con systemd

```bash
# Crear directorio de logs
sudo mkdir -p /var/log/gunicorn
sudo chown www-data:www-data /var/log/gunicorn

# Copiar archivo de servicio
sudo cp deployment/shipping-service.service /etc/systemd/system/

# Recargar systemd
sudo systemctl daemon-reload

# Iniciar servicio
sudo systemctl start shipping-service

# Habilitar en inicio
sudo systemctl enable shipping-service

# Verificar estado
sudo systemctl status shipping-service
```

### 11. Configurar Nginx

```bash
# Copiar configuración
sudo cp deployment/nginx-config /etc/nginx/sites-available/che-shipping

# Crear enlace simbólico
sudo ln -s /etc/nginx/sites-available/che-shipping /etc/nginx/sites-enabled/

# Eliminar sitio por defecto
sudo rm /etc/nginx/sites-enabled/default

# Probar configuración
sudo nginx -t

# Reiniciar Nginx
sudo systemctl restart nginx
```

### 12. Configurar SSL con Let's Encrypt

```bash
# Obtener certificado
sudo certbot --nginx -d envio.chetomi.cl

# Verificar renovación automática
sudo certbot renew --dry-run
```

### 13. Configurar Firewall

```bash
# Permitir puertos necesarios
sudo ufw allow 'Nginx Full'
sudo ufw allow OpenSSH
sudo ufw enable
```

## FASE 3: Verificación

### 14. Probar la aplicación

```bash
# Ver logs de Gunicorn
sudo journalctl -u shipping-service -f

# Ver logs de Nginx
sudo tail -f /var/log/nginx/che-shipping-error.log

# Probar endpoint
curl https://envio.chetomi.cl/shipping/api/methods
```

## 🔄 Actualizar la Aplicación

```bash
cd /var/www/che-shipping

# Pull últimos cambios
sudo -u www-data git pull

# Reinstalar dependencias si es necesario
source venv/bin/activate
pip install -r requirements.txt
deactivate

# Reiniciar servicio
sudo systemctl restart shipping-service
```

## 📊 Monitoreo

```bash
# Estado del servicio
sudo systemctl status shipping-service

# Logs en tiempo real
sudo journalctl -u shipping-service -f

# Uso de recursos
htop

# Logs de Nginx
sudo tail -f /var/log/nginx/che-shipping-access.log
```

## 🐛 Troubleshooting

### Error: No module named 'flask'
```bash
# Verificar que estás usando el venv correcto en systemd
sudo nano /etc/systemd/system/shipping-service.service
# Verificar que Environment="PATH=..." apunta al venv correcto
```

### Error: Connection refused
```bash
# Verificar que Gunicorn está corriendo
sudo systemctl status shipping-service

# Verificar puerto
sudo netstat -tulpn | grep 8000
```

### Error: 502 Bad Gateway
```bash
# Verificar logs de Gunicorn
sudo journalctl -u shipping-service -n 50

# Reiniciar servicio
sudo systemctl restart shipping-service
```

## 🔐 Seguridad

- ✅ Cambiar contraseña de MySQL regularmente
- ✅ Mantener SECRET_KEY seguro y único
- ✅ Actualizar dependencias regularmente: `pip list --outdated`
- ✅ Configurar fail2ban para proteger SSH
- ✅ Revisar logs de acceso regularmente
