#!/bin/bash

# Script to run pytest from a running backend container
# Run locally only and not on servers

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

echo "Running pytest with settings $DJANGO_SETTINGS_MODULE"

if [ "$DJANGO_SETTINGS_MODULE" != "backend.settings.test" ]; then
    echo "Error: Set DJANGO_SETTINGS_MODULE in docker.env to 'backend.settings.test'. Exiting."
    exit 1
fi

echo "Ensure that your docker.env has DJANGO_SETTINGS_MODULE=backend.settings.test"
echo "Enter additional arguments to run pytest:"
read user_command

echo "Running pytest $user_command"

echo "Stopping and removing existing containers"
docker-compose -f ./docker-compose-dev.yml down

echo "Running containers"
docker-compose -f ./docker-compose-dev.yml up -d

docker-compose -f ./docker-compose-dev.yml exec -w /custom_admin_backend/src custom_admin_backend pytest $user_command

echo "Stopping and removing existing containers for testing"
docker-compose -f ./docker-compose-dev.yml down