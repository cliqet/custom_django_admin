from backend.settings.base import IS_DEMO_MODE

from .constants import DASHBOARD_URL_PREFIX

APP_LIST_CONFIG_OVERRIDE = {
    'django_admin': {
        'models': {
            'SavedQueryBuilder': {
                'is_hidden': True
            },
            'SavedRawQuery': {
                'is_hidden': True
            }
        }
    }
}

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

# app_url - This is not really used but it is an option if you want a link and a page
#           for your app
# admin_url - This is the link to the listview page
# add_url - This is the link to the add page

# Sample below of how to override app list config
if IS_DEMO_MODE:
    APP_LIST_CONFIG_OVERRIDE.update({
        # The name of the app
        'django_admin': {
            'app_url': f'{DASHBOARD_URL_PREFIX}/custom',
            'models': {
                # The name of the model
                'Classification': {
                    'admin_url': f'{DASHBOARD_URL_PREFIX}/custom/classification',
                    'add_url': f'{DASHBOARD_URL_PREFIX}/custom/classification/customadd',
                },
                'Level': {
                    'is_hidden': True  # hides the model from the app list
                },
                'SavedQueryBuilder': {
                    'is_hidden': True
                },
                'SavedRawQuery': {
                    'is_hidden': True
                }
                # You can add more models
            },
            # 'is_hidden': True  # hides the app from the app list (all models under are hidden)
        },
        # You can add more apps
    })
