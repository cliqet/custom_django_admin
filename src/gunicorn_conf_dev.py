import os

import toml

env_config = {}

config_filename = os.getenv('CONFIG_FILE', 'config.toml')

with open(os.path.join(os.getcwd(), config_filename)) as f:
    env_config = toml.load(f)

log_dir = env_config.get('logging_config', {}).get('gunicorn_log_path')

wsgi_app="backend.wsgi:application"
loglevel="info"
workers = 4
bind = "0.0.0.0:8000"
timeout = 300
reload = True
accesslog = errorlog = f"{log_dir}/gunicorn.log"
capture_output = True
name = "custom_admin_backend"