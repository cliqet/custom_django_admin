import logging
import os
from enum import Enum
from pathlib import Path

import toml

log = logging.getLogger(__name__)

src_dir = Path(__file__).resolve().parent.parent.parent

config_filename = os.getenv('CONFIG_FILE', 'config.toml')
log.info(f'Loading config file: {config_filename}')

env_config = {}

# Load TOML file
with open(os.path.join(src_dir, config_filename)) as f:
    env_config = toml.load(f)
    log.info('Successfully loaded config file')


class Environment:
    class Application:
        _application_env = env_config.get('application', {})

        protocol: str = _application_env.get('protocol', 'https')
        domain: str = _application_env.get('domain')
        ui_domain: str = _application_env.get('ui_domain')
        is_default_admin_enabled: bool = _application_env.get('is_default_admin_enabled', True)
        media_url: str = _application_env.get('media_url', '/media/')
        media_root: str = _application_env.get('media_root')
        static_url: str = _application_env.get('static_url')
        static_root: str = _application_env.get('static_root')
        secret_key: str = _application_env.get('secret_key')
        debug: bool = _application_env.get('debug')
        use_local_postgres: bool = _application_env.get('use_local_postgres', True)
        use_local_s3: bool = _application_env.get('use_local_s3', True)
        time_zone: str = _application_env.get('time_zone', 'UTC')
        default_email_sender: str = _application_env.get('default_email_sender')
        allowed_hosts: list[str] = _application_env.get('allowed_hosts')
        csrf_trusted_origins: list[str] = _application_env.get('csrf_trusted_origins')
        cors_allowed_origins: list[str] = _application_env.get('cors_allowed_origins')
        cors_allow_credentials: bool = _application_env.get('cors_allow_credentials', False)
        jwt_access_token_life: int = _application_env.get('jwt_access_token_life', 300)
        jwt_refresh_token_life: int = _application_env.get('jwt_refresh_token_life', 3)
        jwt_private_key: str = _application_env.get('jwt_private_key')
        jwt_public_key: str = _application_env.get('jwt_public_key')
        api_max_page_size: int = _application_env.get('max_api_page_size', 20)
        api_permission_classes: list[str] = _application_env.get(
            'api_permission_classes',
            ['rest_framework.permissions.IsAuthenticated']
        )
        api_anon_throttle_rate: int = _application_env.get('api_anon_throttle_rate', 60)
        api_user_throttle_rate: int = _application_env.get('api_user_throttle_rate', 60)
        session_engine: str = _application_env.get('session_engine', '')
        session_cookie_age: int = _application_env.get('session_cookie_age', 1209600)
        password_reset_timeout: int = _application_env.get('password_reset_timeout', 86400)
        csrf_trusted_origins: list[str] = _application_env.get('csrf_trusted_origins')
        brand_name: str = _application_env.get('brand_name', 'CUSTOM DJANGO ADMIN')

        
    class LoggingConfig:
        _logging_config_env = env_config.get('logging_config', {})

        handlers: list[str] = _logging_config_env.get('handlers', ['console'])
        gunicorn_log_path: str = _logging_config_env.get('gunicorn_log_path')

        class FileHandler:
            _file_handler_env = env_config.get('logging_config', {}).get('file_handler', {})

            log_level: str = _file_handler_env.get('log_level')
            log_path: str = _file_handler_env.get('log_path')
            max_bytes: int = _file_handler_env.get('max_bytes')
            backup_count: int = _file_handler_env.get('backup_count')

        class ConsoleHandler:
            _console_handler_env = env_config.get('logging_config', {}).get('console_handler', {})

            log_level: str = _console_handler_env.get('log_level')

        file_handler = FileHandler()
        console_handler = ConsoleHandler()


    class Integration:
        class AWS:
            _aws_env = env_config.get('integration', {}).get('aws', {})

            access_key: str = _aws_env.get('access_key')
            secret_key: str = _aws_env.get('secret_key')
            region: str = _aws_env.get('region')
            media_files_bucket: str = _aws_env.get('media_files_bucket')
            private_files_bucket = _aws_env.get('private_files_bucket')


        class Smtp2Go:
            _smtp2go_env = env_config.get('integration', {}).get('smtp2go', {})

            api_url = _smtp2go_env.get('api_url')
            api_key: str = _smtp2go_env.get('api_key')


        class Cloudflare:
            _cloudflare_env = env_config.get('integration', {}).get('cloudflare', {})

            site_key: str = _cloudflare_env.get('site_key')
            secret_key: str = _cloudflare_env.get('secret_key')
            verify_api_url: str = _cloudflare_env.get('verify_api_url')

        aws = AWS()
        smtp = Smtp2Go()
        cloudflare = Cloudflare()


    class Database:
        class PSQL:
            _psql_env = env_config.get('database', {}).get('psql', {})

            db_name: str = _psql_env.get('db_name')
            db_port: int = _psql_env.get('db_port')
            db_host: str = _psql_env.get('db_host')
            db_user: str = _psql_env.get('db_user')
            db_password: str = _psql_env.get('db_password')

        class Redis:
            _redis_env = env_config.get('database', {}).get('redis', {})

            host: str = _redis_env.get('host')
            username: str = _redis_env.get('username')
            password: str = _redis_env.get('password')
            port: int = _redis_env.get('port')
            db_index: int = _redis_env.get('db_index')
            test_db_index: int = _redis_env.get('test_db_index')

        psql = PSQL()
        redis = Redis()

    application = Application()
    logging_config = LoggingConfig()
    integration = Integration()
    database = Database()

env = Environment()

class DjangoSettings(Enum):
    LOCAL = 'LOCAL'
    TEST = 'TEST'
    STAGING = 'STAGING'
    PROD = 'PROD'