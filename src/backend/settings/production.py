# ruff: noqa: F403, F405
import logging

from backend.settings.base import *

log = logging.getLogger(__name__)

SECURE_HSTS_SECONDS = 120
CSRF_COOKIE_SECURE = True
SESSION_COOKIE_SECURE = True


# Ensure it is always using s3
AWS_ACCESS_KEY_ID = ENV.integration.aws.access_key
AWS_SECRET_ACCESS_KEY = ENV.integration.aws.secret_key
AWS_STORAGE_BUCKET_NAME = ENV.integration.aws.media_files_bucket
AWS_S3_REGION_NAME = ENV.integration.aws.region
AWS_S3_CUSTOM_DOMAIN = f'{AWS_STORAGE_BUCKET_NAME}.s3.{AWS_S3_REGION_NAME}.amazonaws.com'
AWS_S3_FILE_OVERWRITE = False

AWS_LOCATION_MEDIA = 'media'
MEDIA_URL = f'https://{AWS_S3_CUSTOM_DOMAIN}/{AWS_LOCATION_MEDIA}/'

AWS_LOCATION_STATIC = 'static'
STATIC_URL = f'https://{AWS_S3_CUSTOM_DOMAIN}/{AWS_LOCATION_STATIC}/'

STORAGES = {
    # For media uploaded files
    'default': {
        'BACKEND': 'storages.backends.s3.S3Storage'
    },
    # For static files
    'staticfiles': {
        'BACKEND': 'storages.backends.s3.S3Storage'
    }
}

AWS_STORAGE_BUCKET_NAME_PRIVATE = ENV.integration.aws.private_files_bucket
AWS_S3_CUSTOM_DOMAIN_PRIVATE = f'{AWS_STORAGE_BUCKET_NAME_PRIVATE}.s3.{AWS_S3_REGION_NAME}.amazonaws.com'


# Ensure database always use postgres or production db choice
DATABASES = {
    "default": {
        "ENGINE": "django.db.backends.postgresql",
        "NAME": ENV.database.psql.db_name,
        "PORT": ENV.database.psql.db_port,
        "HOST": ENV.database.psql.db_host,
        "USER": ENV.database.psql.db_user,
        "PASSWORD": ENV.database.psql.db_password
    },
}

log.info(f'Production settings loaded')