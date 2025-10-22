# Configuración de Gunicorn para producción
import multiprocessing

# Dirección y puerto
bind = "127.0.0.1:8000"

# Workers (número de procesos)
# Recomendado: (2 x núcleos CPU) + 1
workers = multiprocessing.cpu_count() * 2 + 1

# Tipo de worker
worker_class = "sync"

# Timeout (segundos)
timeout = 120

# Logs
accesslog = "/var/log/gunicorn/access.log"
errorlog = "/var/log/gunicorn/error.log"
loglevel = "info"

# Reiniciar workers automáticamente
max_requests = 1000
max_requests_jitter = 50

# Daemon
daemon = False
