# from .constants import DASHBOARD_URL_PREFIX

APP_LIST_CONFIG_OVERRIDE = {}

# This example below shows how to override the app list so that you can use
# a different url for the specific app.model.
# If you want to override every app and models you registered, better to 
# create your own custom views for each and do not use the provided generic routes
# in the UI
# APP_LIST_CONFIG_OVERRIDE = {
#     # The name of the app
#     'demo': {
#         'app_url': f'{DASHBOARD_URL_PREFIX}/custom',
#         'models': {
#             # The name of the model
#             'Classification': {
#                 'admin_url': f'{DASHBOARD_URL_PREFIX}/custom/classification',
#                 'add_url': f'{DASHBOARD_URL_PREFIX}/custom/classification/customadd',
#             },
#             # You can add more models
#         }
#     },
#     # You can add more apps
# }