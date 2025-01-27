from django.http import HttpRequest
from django.utils.deprecation import MiddlewareMixin
from django.views.defaults import permission_denied

from backend.settings.base import ENV


class CustomMiddleware(MiddlewareMixin):
    def process_request(self, request: HttpRequest):
        if not ENV.application.is_default_admin_enabled and request.path.startswith('/admin'):
            return permission_denied(request, 'You don’t have permission to access this page')

    def process_response(self, request, response):
        return response
    


