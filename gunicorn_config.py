# Configuración de Gunicorn para producción
import multiprocessing
import os

# Dirección y puerto
# En Docker, bind a 0.0.0.0 para que sea accesible desde fuera del contenedor
bind = "0.0.0.0:8000"

# Workers (número de procesos)
# En Docker/Easypanel, usar menos workers
workers = int(os.environ.get('GUNICORN_WORKERS', multiprocessing.cpu_count() * 2 + 1))

# Tipo de worker
worker_class = "sync"

# Timeout (segundos)
timeout = 120

# Logs (en Docker, enviar a stdout/stderr)
accesslog = "-"  # stdout
errorlog = "-"   # stderr
loglevel = os.environ.get('LOG_LEVEL', 'info')

# Reiniciar workers automáticamente
max_requests = 1000
max_requests_jitter = 50

# Daemon
daemon = False

# Pre-load app para mejor performance
preload_app = True
