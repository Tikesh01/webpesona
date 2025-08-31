# Gunicorn configuration file
import multiprocessing

# Binding
bind = "0.0.0.0:10000"  # Render will override the port anyway

# Worker processes
workers = multiprocessing.cpu_count() * 2 + 1
worker_class = 'sync'
worker_connections = 1000
timeout = 120
keepalive = 2

# Logging
accesslog = '-'
errorlog = '-'
loglevel = 'info'

# Process naming
proc_name = 'webpersona'

# SSL (if needed)
keyfile = None
certfile = None
