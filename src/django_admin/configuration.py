from backend.settings.base import APP_MODE, DjangoSettings

# from .constants import DASHBOARD_URL_PREFIX

APP_LIST_CONFIG_OVERRIDE = {}

# This example below shows how to override the app list so that you can use
# a different url for the specific app.model.
# If you want to override every app and models you registered, better to 
# create your own custom views for each and do not use the provided generic routes
# in the UI
# Optional overrides for apps
# - app_url
# - is_hidden
# - models
#
# Optional overrides for models
# - admin_url
# - add_url

"""
Example of overriding:
APP_LIST_CONFIG_OVERRIDE = {
    # The name of the app
    'demo': {
        'app_url': f'{DASHBOARD_URL_PREFIX}/custom',
        'models': {
            # The name of the model
            'Classification': {
                'admin_url': f'{DASHBOARD_URL_PREFIX}/custom/classification',
                'add_url': f'{DASHBOARD_URL_PREFIX}/custom/classification/customadd',
            },
            'Level': {
                'is_hidden': True  # hides the model from the app list
            }
            # You can add more models
        },
        # 'is_hidden': True  # hides the app from the app list (all models under are hidden)
    },
    # You can add more apps
}
"""

# Do not override demo app for pytest
# If you want to delete demo from the whole application, you must remove all 
# references to it including the tests
if APP_MODE == DjangoSettings.TEST and APP_LIST_CONFIG_OVERRIDE.get('demo'):
    del APP_LIST_CONFIG_OVERRIDE['demo']