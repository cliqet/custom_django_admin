from datetime import timedelta


def get_file(file_url: str) -> str | None:
    """ Will raise an error if the file is not found """
    with open(file_url) as f:
        return f.read()


def get_jwt_config(ENV: dict) -> dict:
    return {
        'ACCESS_TOKEN_LIFETIME': timedelta(minutes=ENV.application.jwt_access_token_life),
        'REFRESH_TOKEN_LIFETIME': timedelta(days=ENV.application.jwt_refresh_token_life),
        'ROTATE_REFRESH_TOKENS': True,  # True gives a new refresh token every refresh
        'BLACKLIST_AFTER_ROTATION': True,  # True makes sure old refresh token cannot be used anymore

        # Custom token serializer
        "TOKEN_OBTAIN_SERIALIZER": "django_admin_users.serializers.AdminUserObtainPairSerializer",

        # 'ALGORITHM': 'HS256',
        'ALGORITHM': 'RS256',
        'SIGNING_KEY': get_file(ENV.application.jwt_private_key),
        'VERIFYING_KEY': get_file(ENV.application.jwt_public_key),
        'ISSUER': 'SolidDjango',

        'AUTH_HEADER_TYPES': ('Bearer',),
        'USER_ID_FIELD': 'uid',
        'AUTH_TOKEN_CLASSES': ('rest_framework_simplejwt.tokens.AccessToken',),
        'JTI_CLAIM': 'jti',
    }