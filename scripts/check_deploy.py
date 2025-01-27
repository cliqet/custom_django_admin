"""
    Checks the setup depending on the environment. Run this in root directory.
    Activate your virtual environment and run:
    python ./scripts/check_deploy.py 
"""
import os
import sys

import toml
from check_config import is_config_complete


def has_keys(cwd: str) -> bool:
    keys_dir = os.path.join(cwd, 'keys')
    if (
        os.path.isdir(keys_dir) and 
        os.path.isfile(os.path.join(keys_dir, 'jwt_private.pem')) and 
        os.path.isfile(os.path.join(keys_dir, 'jwt_public.pub'))
    ):
        return True
    return False


def run() -> None:
    root_dir = os.getcwd()

    print('Which mode are you running the application with?')
    print('p. Python\nd. Docker')
    mode = input('Enter mode: [p / d]: ')
    if mode not in ['p', 'd']:
        print('Invalid mode')
        sys.exit(1)

    print()
    if mode == 'd':
        print('Which environment?')
        # NOTE: Assumes you have Staging and Production aside from dev/local
        print('L. Local\ns. Staging\np. Production')

        environment = input('Enter mode: [L / s / p]: ')
        if environment not in ['L', 's', 'p']:
            print('Invalid environment')
            sys.exit(1)
    else:
        environment = 'L'

    print()
    # if running using python in local
    if mode == 'p':
        with open(os.path.join(root_dir, 'src', 'config.toml'), 'r') as file:
            config_file = toml.load(file)
            
            print('Checking config file variables against template')
            complete = is_config_complete('config.toml')
            if not complete:
                print('Config variables not complete')
                sys.exit(1)
            print()

            print('Checking paths set in config file')
            static_root = config_file['application']['static_root']
            log_path = config_file['logging_config']['file_handler']['log_path']

            if static_root == os.path.join(root_dir, 'static'):
                print('Invalid static root path. Do not point to src.static directory')
                sys.exit(1)

            if log_path != os.path.join(root_dir, 'src', 'logs', 'app'):
                print('Incorrect log path.')
                sys.exit(1)

            print('Checking jwt keys')
            if not has_keys(root_dir):
                print('Missing keys')
                sys.exit(1)
            print()


    # if running using docker in local
    if mode == 'd' and environment == 'L':
        with open(os.path.join(root_dir, 'src', 'docker.config.toml'), 'r') as file:
            config_file = toml.load(file)
            
            print('Checking config file variables against template')
            complete = is_config_complete('docker.config.toml')
            if not complete:
                print('Config variables not complete')
                sys.exit(1)
            print()

            # NOTE: This is not a complete check but should have the important ones
            # Always check the config template for guidance
            print('Checking variables set in config file')
            jwt_private_key = config_file['application']['jwt_private_key']
            jwt_public_key = config_file['application']['jwt_public_key']
            static_root = config_file['application']['static_root']
            log_path = config_file['logging_config']['file_handler']['log_path']
            media_root = config_file['application']['media_root']
            use_local_s3 = config_file['application']['use_local_s3']
            gunicorn_log_path = config_file['logging_config']['gunicorn_log_path']

            if jwt_private_key != '/custom_admin_backend/keys/jwt_private.pem':
                print('Incorrect jwt_private_key path')
                sys.exit(1)

            if jwt_public_key != '/custom_admin_backend/keys/jwt_public.pub':
                print('Incorrect jwt_public_key path')
                sys.exit(1)

            if not use_local_s3 and media_root != '/var/www/media':
                print('Invalid media root')
                sys.exit(1)

            if not use_local_s3 and static_root != '/var/www/static':
                print('Invalid static root')
                sys.exit(1)


            if log_path != '/custom_admin_backend/src/logs/app':
                print('Incorrect log path.')
                sys.exit(1)

            if gunicorn_log_path != '/var/log/gunicorn':
                print('Incorrect gunicorn log path.')
                sys.exit(1)

            print()
            print('Checking jwt keys')
            if not has_keys(root_dir):
                print('Missing keys')
                sys.exit(1)
            print()

            print('Checking docker.env file')
            with open(os.path.join(root_dir, 'docker.env'), 'r') as env_file:
                for line in env_file.readlines():
                    env_var, env_val = line.strip().split('=')
                    if env_var == 'DJANGO_SETTINGS_MODULE' and env_val != 'backend.settings.base':
                        print('Invalid DJANGO_SETTINGS_MODULE')
                        sys.exit(1)

                    if env_var == 'CONFIG_FILE' and env_val != 'docker.config.toml':
                        print('Invalid CONFIG_FILE')
                        sys.exit(1)


            print()
            print('Setup OK')

    

if __name__ == '__main__':
    run()