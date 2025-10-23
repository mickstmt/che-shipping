# Despliegue en Producción con Sistema de Login

## Pasos para Actualizar en Easypanel

### 1. Redeploy de la Aplicación

1. Entra a **Easypanel** en tu navegador
2. Ve a tu aplicación **`che-shipping`**
3. Click en **"Deploy"** o **"Redeploy"**
4. Espera 2-3 minutos mientras:
   - Descarga el código actualizado de GitHub
   - Reconstruye la imagen Docker
   - Reinicia la aplicación

### 2. Crear la Tabla `admin_users` en Producción

Una vez desplegado, necesitas crear la tabla en la base de datos de producción:

#### Opción A - Desde Easypanel Console (Recomendado)

1. En Easypanel, ve a tu aplicación **`che-shipping`**
2. Click en la pestaña **"Console"** o **"Terminal"**
3. Ejecuta:
   ```bash
   python create_admin_table.py
   ```
4. Deberías ver: `[OK] Tabla admin_users creada exitosamente!`

#### Opción B - Desde MySQL Directo

1. Ve al servicio **`shipping-mysql`** en Easypanel
2. Click en **"Console"**
3. Ejecuta:
   ```bash
   mysql -u mickstmt -p shipping_chile
   ```
4. Ingresa la password (la que te dio Easypanel)
5. Pega y ejecuta:
   ```sql
   CREATE TABLE IF NOT EXISTS admin_users (
       id INT AUTO_INCREMENT PRIMARY KEY,
       username VARCHAR(50) UNIQUE NOT NULL,
       password_hash VARCHAR(255) NOT NULL,
       is_active BOOLEAN DEFAULT TRUE,
       created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
       last_login DATETIME,
       INDEX idx_username (username),
       INDEX idx_active (is_active)
   ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;
   ```

### 3. Crear tu Primer Usuario Admin

Una vez creada la tabla, crea tu usuario administrador:

#### Opción A - Usuario por Defecto (Rápido)

Desde la console de la app en Easypanel:
```bash
python create_first_admin.py
```

Esto crea:
- **Username**: `admin`
- **Password**: `admin123`

**⚠️ IMPORTANTE**: Cambia esta contraseña después del primer login.

#### Opción B - Usuario Personalizado (Recomendado)

Desde la console de la app en Easypanel:
```bash
python create_admin_user.py
```

Menú interactivo:
```
1. Crear nuevo administrador  ← Selecciona esto
2. Listar administradores
3. Desactivar administrador
4. Salir
```

Te pedirá:
- **Username**: (el que quieras, ej: `andree`)
- **Password**: (mínimo 6 caracteres)
- **Confirmar password**

### 4. Verificar que Funciona

1. Abre: **https://envio.chetomi.cl/shipping/**
2. Deberías ser redirigido a: **https://envio.chetomi.cl/shipping/login**
3. Ingresa tus credenciales
4. Deberías ver el panel admin con tu nombre arriba a la derecha

### 5. Verificar APIs Públicas (NO requieren login)

Estas URLs deben funcionar SIN login:
- https://envio.chetomi.cl/shipping/api/jumpseller/services
- https://envio.chetomi.cl/shipping/api/jumpseller/callback (POST)

---

## 🔐 Gestión de Usuarios Admin

### Crear Más Usuarios

Desde la console de Easypanel:
```bash
python create_admin_user.py
```

Selecciona opción 1 y sigue las instrucciones.

### Listar Usuarios Existentes

```bash
python create_admin_user.py
```

Selecciona opción 2 para ver todos los usuarios admin.

### Desactivar un Usuario

```bash
python create_admin_user.py
```

Selecciona opción 3 e ingresa el username a desactivar.

**Nota**: Desactivar NO elimina el usuario, solo impide que inicie sesión.

---

## 🔒 Seguridad

### ✅ Lo que está protegido (Requiere Login)

- `/shipping/` - Panel principal
- `/shipping/admin/methods` - Gestión de métodos
- `/shipping/admin/zones` - Gestión de zonas
- Todas las rutas `/shipping/admin/*`

### ✅ Lo que NO está protegido (APIs Públicas)

- `/shipping/api/jumpseller/callback` - Jumpseller callback
- `/shipping/api/jumpseller/services` - Jumpseller services
- `/shipping/api/quote` - API de cotización pública

Jumpseller y otras integraciones externas **NO se ven afectadas** por el login.

---

## 🛠️ Troubleshooting

### Error: "No module named 'flask_login'"

La aplicación necesita reinstalar dependencias. Esto no debería pasar con Docker, pero si ocurre:

1. Verifica que `requirements.txt` tenga:
   ```
   Flask-Login==0.6.3
   ```
2. Redeploy en Easypanel (reconstruye la imagen)

### Error: "Table 'admin_users' doesn't exist"

Ejecuta el paso 2 para crear la tabla:
```bash
python create_admin_table.py
```

### Olvidé mi Contraseña

Desde la console de Easypanel:
```bash
python create_admin_user.py
```

Opción 3: Desactiva el usuario viejo
Opción 1: Crea un nuevo usuario

O puedes resetear el password desde MySQL directamente (necesitarás generar un hash).

### No Puedo Acceder a la Console de Easypanel

Contacta a Easypanel support o accede vía SSH a tu VPS y ejecuta:
```bash
docker exec -it <container_name> python create_first_admin.py
```

---

## 📝 Checklist de Deployment

- [ ] Redeploy en Easypanel
- [ ] Crear tabla `admin_users`
- [ ] Crear primer usuario admin
- [ ] Probar login en https://envio.chetomi.cl/shipping/login
- [ ] Verificar que panel admin funcione
- [ ] Verificar que APIs públicas funcionen (Jumpseller)
- [ ] Crear usuarios adicionales si es necesario

---

## 🎯 Resumen de Comandos

```bash
# Crear tabla admin_users
python create_admin_table.py

# Crear usuario admin/admin123 (rápido)
python create_first_admin.py

# Menú interactivo para gestionar usuarios
python create_admin_user.py
```

---

¡Listo! Ahora tu panel admin está protegido con login mientras que las APIs públicas siguen funcionando sin restricciones.
