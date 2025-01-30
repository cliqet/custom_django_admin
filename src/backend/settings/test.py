from .base import *  # noqa: F403

DEBUG = True

LOGGING = None

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.sqlite3',
        'NAME': BASE_DIR / 'sqlite_dbs' / 'db_test.sqlite3',   
    }
}


prefix_auth = ''
if ENV.database.redis.password:
    prefix_auth += f':{ENV.database.redis.password}@'

if ENV.database.redis.username:
    prefix_auth = ENV.database.redis.username + prefix_auth

redis_location = f'redis://{prefix_auth}{ENV.database.redis.host}:{ENV.database.redis.port}/{ENV.database.redis.test_db_index}'

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
        'DB': ENV.database.redis.test_db_index,
        'USERNAME': ENV.database.redis.username,
        'PASSWORD': ENV.database.redis.password,
        'DEFAULT_TIMEOUT': 360,
    },
}


