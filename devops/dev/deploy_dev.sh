#!/bin/bash

# NOTE: pull branch manually to work with. Automate when on servers

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

ROOT_DIR="$(cd "$SCRIPT_DIR/../.." && pwd)"
echo "Deploy script root directory: $ROOT_DIR"

set -a
source "$ROOT_DIR/docker.env"
set +a

echo "Deploy script: DJANGO_SETTINGS_MODULE = $DJANGO_SETTINGS_MODULE"
echo "Deploy script: CONFIG FILE = $CONFIG_FILE"  

if [ "$DJANGO_SETTINGS_MODULE" != "backend.settings.base" ]; then
    echo "ERROR: Set DJANGO_SETTINGS_MODULE to backend.settings.base"
    exit 1
fi

cd $ROOT_DIR

echo "Moved to directory: $ROOT_DIR"

echo "Stopping and removing existing containers"
docker-compose -f ./docker-compose-dev.yml down

echo "Building the Nginx image"
docker-compose -f ./docker-compose-dev.yml build custom_admin_nginx

echo "Building the Backend image"
docker-compose -f ./docker-compose-dev.yml build custom_admin_backend

# NOTE: Remove if you will be using a different async task manager
echo "Building the Queue Worker image"
docker-compose -f ./docker-compose-dev.yml build custom_admin_worker

echo "Running containers"
docker-compose -f ./docker-compose-dev.yml up -d

echo "Running migrations"
docker-compose -f ./docker-compose-dev.yml exec -w /custom_admin_backend/src custom_admin_backend python3 manage.py migrate

echo "Running collectstatic"
docker-compose -f ./docker-compose-dev.yml exec -w /custom_admin_backend/src custom_admin_backend python3 manage.py collectstatic --noinput

# Show logs in case containers fail to start
echo
echo "Custom Admin Backend Logs ***************************************"
docker-compose -f ./docker-compose-dev.yml logs --tail=10 custom_admin_backend
echo "End of Custom Admin Backend Logs ********************************"
echo

echo "Custom Admin Redis Logs ***************************************"
docker-compose -f ./docker-compose-dev.yml logs --tail=10 custom_admin_redis
echo "End of Custom Admin Redis Logs ********************************"
echo

# NOTE: Remove if you will be using a different async task manager
echo "Custom Admin Worker Logs ***************************************"
docker-compose -f ./docker-compose-dev.yml logs --tail=10 custom_admin_worker
echo "End of Custom Admin Worker Logs ********************************"
echo

echo "Custom Admin Nginx Logs ****************************************"
docker-compose -f ./docker-compose-dev.yml logs --tail=10 custom_admin_nginx
echo "End of Custom Admin Nginx Logs *********************************"
echo

echo "Custom Admin DB Logs *******************************************"
docker-compose -f ./docker-compose-dev.yml logs --tail=10 custom_admin_db
echo "End of Custom Admin DB Logs ************************************"
echo 

# Clean up every now and then especially when changes are made to Dockerfiles
# Free up space from image accumulation
echo "Do you want to remove unused images? [y/N]:"
read is_remove
if [[ $is_remove == [yY] ]]; then
    docker image prune -a
    echo "Removed unused images"
else
    echo "Unused images removal skipped."
fi


