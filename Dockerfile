# Dockerfile para Che Shipping Service
FROM python:3.11-slim

# Variables de entorno para Python
ENV PYTHONUNBUFFERED=1 \
    PYTHONDONTWRITEBYTECODE=1 \
    PIP_NO_CACHE_DIR=1 \
    PIP_DISABLE_PIP_VERSION_CHECK=1

# Instalar dependencias del sistema
RUN apt-get update && apt-get install -y \
    gcc \
    default-libmysqlclient-dev \
    pkg-config \
    && rm -rf /var/lib/apt/lists/*

# Crear directorio de trabajo
WORKDIR /app

# Copiar requirements y instalar dependencias Python
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copiar el código de la aplicación
COPY . .

# Crear directorio para logs
RUN mkdir -p /var/log/gunicorn && \
    chmod 755 /var/log/gunicorn

# Exponer puerto
EXPOSE 8000

# Usuario no-root para seguridad
RUN useradd -m -u 1000 appuser && \
    chown -R appuser:appuser /app /var/log/gunicorn

USER appuser

# Comando de inicio
CMD ["gunicorn", "--config", "gunicorn_config.py", "run:app"]
