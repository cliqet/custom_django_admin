#!/bin/bash

# Check if /usr/bin/bash exists and is executable
# because /usr/bin/bash is used in the container
if [ -x /usr/bin/bash ]; then
    BASH_EXEC="/usr/bin/bash"
else
    BASH_EXEC="/bin/bash"
fi

set -e

# Get the directory of the script
SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"
echo "Deploy script current directory: $SCRIPT_DIR"

ROOT_DIR="$(cd "$SCRIPT_DIR/.." && pwd)"
echo "Deploy script root directory: $ROOT_DIR"

set -a
source "$ROOT_DIR/docker.env"
set +a

echo "Run script: DJANGO_SETTINGS_MODULE = $DJANGO_SETTINGS_MODULE"
echo "Run script: CONFIG FILE = $CONFIG_FILE"  

cd "$ROOT_DIR/src"
echo "Switching to src directory"

# NOTE: Remove if you want to use a different async task manager
if [[ $1 == 'admin-backend' ]]; then
    echo "Running backend"
    gunicorn -c ./gunicorn_conf_dev.py backend.wsgi
fi

if [[ $1 == 'rq-worker' ]]; then
    echo "Running rq worker"
    python3 manage.py rqworker default
fi

