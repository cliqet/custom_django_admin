#!/bin/bash

# Script to run manage.py from a running backend container
#. E.g. entering showmigrations will run manage.py showmigrations
# on the backend container
# just run from root directory ./scripts/run_manage_py.sh

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

echo "Deploy script: DJANGO_SETTINGS_MODULE = $DJANGO_SETTINGS_MODULE" 
echo "Deploy script: CONFIG FILE = $CONFIG_FILE"

MODE="prod"
if [ "$DJANGO_SETTINGS_MODULE" = "backend.settings.base" ]; then
    MODE="dev"
fi

echo "Running in $MODE mode"

echo "Enter command to run with manage.py:"
read user_command

echo "Running python3 manage.py $user_command"

docker-compose -f ./docker-compose-"$MODE".yml exec -w /custom_admin_backend/src custom_admin_backend python3 manage.py $user_command

