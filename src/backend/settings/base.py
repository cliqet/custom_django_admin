import logging
import os
from pathlib import Path

from .environment import DjangoSettings, env
from .jwt import get_jwt_config
from .logging import get_logging_config

ENV = env

# Logging Configuration
LOGGING = get_logging_config(ENV)

log = logging.getLogger(__name__)

APP_MODE = DjangoSettings.LOCAL

MODES = {
    'backend.settings.base': DjangoSettings.LOCAL,
    'backend.settings.test': DjangoSettings.TEST,
    'backend.settings.staging': DjangoSettings.STAGING,
    'backend.settings.prod': DjangoSettings.PROD
}

django_settings_module = os.environ.get('DJANGO_SETTINGS_MODULE')
if django_settings_module:
    APP_MODE = MODES[django_settings_module]


# Build paths inside the project like this: BASE_DIR / 'subdir'.
BASE_DIR = Path(__file__).resolve().parent.parent.parent


# Quick-start development settings - unsuitable for production
# See https://docs.djangoproject.com/en/5.1/howto/deployment/checklist/

# SECURITY WARNING: keep the secret key used in production secret!
SECRET_KEY = ENV.application.secret_key

# SECURITY WARNING: don't run with debug turned on in production!
DEBUG = ENV.application.debug

ALLOWED_HOSTS = ENV.application.allowed_hosts


# Application definition

INSTALLED_APPS = [
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',

    # external libraries
    'django_extensions',
    'rest_framework',
    'rest_framework_simplejwt.token_blacklist',
    'corsheaders',
    'storages',
    'django_rq',
    'drf_spectacular',

    # user-defined apps
    'django_admin',
    'users',
    'documentation',
    'demo', # For demo purposes only. Delete this!!!!!
]

AUTH_USER_MODEL = 'users.CustomUser'

# DRF settings
REST_FRAMEWORK = {
    'DEFAULT_SCHEMA_CLASS': 'drf_spectacular.openapi.AutoSchema',
    'DEFAULT_AUTHENTICATION_CLASSES': [
        'rest_framework_simplejwt.authentication.JWTAuthentication',
        'rest_framework.authentication.SessionAuthentication'
    ],
    'DEFAULT_THROTTLE_CLASSES': [
        'rest_framework.throttling.AnonRateThrottle',
        'rest_framework.throttling.UserRateThrottle'
    ],
    'DEFAULT_THROTTLE_RATES': {
        'anon': f'{ENV.application.api_anon_throttle_rate}/minute',
        'user': f'{ENV.application.api_user_throttle_rate}/minute'
    },
    'DEFAULT_PERMISSION_CLASSES': [
        'django_admin.permissions.IsFromUiRequest',
        *ENV.application.api_permission_classes
    ],
    'DEFAULT_PAGINATION_CLASS': 'rest_framework.pagination.LimitOffsetPagination',
    'PAGE_SIZE': ENV.application.api_max_page_size,
}

CORS_ALLOWED_ORIGINS = ENV.application.cors_allowed_origins
CORS_ALLOW_CREDENTIALS = True

# JWT settings
SIMPLE_JWT = get_jwt_config(ENV)

MIDDLEWARE = [
    'corsheaders.middleware.CorsMiddleware',

    'django.middleware.security.SecurityMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
    'backend.middleware.CustomMiddleware',
]

ROOT_URLCONF = 'backend.urls'

TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [],
        'APP_DIRS': True,
        'OPTIONS': {
            'context_processors': [
                'django.template.context_processors.debug',
                'django.template.context_processors.request',
                'django.contrib.auth.context_processors.auth',
                'django.contrib.messages.context_processors.messages',
            ],
        },
    },
]

WSGI_APPLICATION = 'backend.wsgi.application'


# Database
# https://docs.djangoproject.com/en/5.1/ref/settings/#databases

if ENV.application.use_local_postgres:
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
else:
    DATABASES = {
        'default': {
            'ENGINE': 'django.db.backends.sqlite3',
            'NAME': BASE_DIR / 'sqlite_dbs' / 'db.sqlite3',
        }
    }


# Password validation
# https://docs.djangoproject.com/en/5.1/ref/settings/#auth-password-validators

AUTH_PASSWORD_VALIDATORS = [
    {
        'NAME': 'django.contrib.auth.password_validation.UserAttributeSimilarityValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.MinimumLengthValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.CommonPasswordValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.NumericPasswordValidator',
    },
]

# Sessions used in django admin only
# https://docs.djangoproject.com/en/5.1/topics/http/sessions/
if ENV.application.session_engine:
    SESSION_ENGINE = ENV.application.session_engine

SESSION_COOKIE_AGE = ENV.application.session_cookie_age


# Cache settings
# https://docs.djangoproject.com/en/5.1/topics/cache/

prefix_auth = ''
if ENV.database.redis.password:
    prefix_auth += f':{ENV.database.redis.password}@'

if ENV.database.redis.username:
    prefix_auth = ENV.database.redis.username + prefix_auth

redis_location = f'redis://{prefix_auth}{ENV.database.redis.host}:{ENV.database.redis.port}/{ENV.database.redis.db_index}'

CACHES = {
    "default": {
        "BACKEND": "backend.settings.redis.RedisCache",
        "LOCATION": redis_location,
    },
}

RQ_QUEUES = {
    'default': {
        'HOST': ENV.database.redis.host,
        'PORT': ENV.database.redis.port,
        'DB': ENV.database.redis.db_index,
        'USERNAME': ENV.database.redis.username,
        'PASSWORD': ENV.database.redis.password,
        'DEFAULT_TIMEOUT': 360,
    },
}

# Internationalization
# https://docs.djangoproject.com/en/5.1/topics/i18n/

LANGUAGE_CODE = 'en-us'

TIME_ZONE = ENV.application.time_zone

USE_I18N = True

USE_TZ = True


# Static files (CSS, JavaScript, Images)
# https://docs.djangoproject.com/en/4.1/howto/static-files/
STATIC_URL = ENV.application.static_url

# This is ignored when using s3
STATIC_ROOT = ENV.application.static_root

STATICFILES_DIRS = [BASE_DIR / 'static']

MEDIA_ROOT = ENV.application.media_root

if ENV.application.use_local_s3:
    AWS_ACCESS_KEY_ID = ENV.integration.aws.access_key
    AWS_SECRET_ACCESS_KEY = ENV.integration.aws.secret_key
    AWS_STORAGE_BUCKET_NAME = ENV.integration.aws.media_files_bucket
    AWS_S3_REGION_NAME = ENV.integration.aws.region
    AWS_S3_CUSTOM_DOMAIN = f'{AWS_STORAGE_BUCKET_NAME}.s3.{AWS_S3_REGION_NAME}.amazonaws.com'
    AWS_S3_FILE_OVERWRITE = False

    AWS_LOCATION_MEDIA = 'media'
    MEDIA_URL = f'https://{AWS_S3_CUSTOM_DOMAIN}/{AWS_LOCATION_MEDIA}/'

    STORAGES = {
        # For media uploaded files, this will allow us to use existing files
        # in s3 which makes it useful when we just get a dump of a server's db
        'default': {
            'BACKEND': 'storages.backends.s3.S3Storage'
        },
        # For static files, just use your local static root
        'staticfiles': {
            'BACKEND': 'django.contrib.staticfiles.storage.ManifestStaticFilesStorage'
        }
    }

    AWS_STORAGE_BUCKET_NAME_PRIVATE = ENV.integration.aws.private_files_bucket
    AWS_S3_CUSTOM_DOMAIN_PRIVATE = f'{AWS_STORAGE_BUCKET_NAME_PRIVATE}.s3.{AWS_S3_REGION_NAME}.amazonaws.com'
else:
    MEDIA_URL = ENV.application.media_url

    STORAGES = {
        "default": {
            "BACKEND": "django.core.files.storage.FileSystemStorage",
        },
        "staticfiles": {
            "BACKEND": "django.contrib.staticfiles.storage.ManifestStaticFilesStorage",
        },
    }

# Default primary key field type
# https://docs.djangoproject.com/en/5.1/ref/settings/#default-auto-field

DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'

# For api docs
SPECTACULAR_SETTINGS = {
    'TITLE': 'Django Custom Admin',
    'DESCRIPTION': 'Admin API Documentation',
    'VERSION': '1.0.0',
}


# SMTP settings. Adjust for SMTP provider
SMTP_API_URL = ENV.integration.smtp.api_url
SMTP_API_KEY = ENV.integration.smtp.api_key


PASSWORD_RESET_TIMEOUT = ENV.application.password_reset_timeout

PROTOCOL = ENV.application.protocol
DOMAIN = ENV.application.domain
UI_DOMAIN = ENV.application.ui_domain


# Cloudflare
CLOUDFLARE_TURNSTILE_SITE_KEY = ENV.integration.cloudflare.site_key
CLOUDFLARE_TURNSTILE_SECRET_KEY = ENV.integration.cloudflare.secret_key
CLOUDFLARE_TURNSTILE_VERIFY_URL = ENV.integration.cloudflare.verify_api_url

CSRF_TRUSTED_ORIGINS = ENV.application.csrf_trusted_origins

log.info('Base settings loaded')

