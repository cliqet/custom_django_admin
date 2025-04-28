from django.conf.urls.static import static
from django.contrib import admin
from django.urls import include, path
from drf_spectacular.views import (
    SpectacularAPIView,
    SpectacularRedocView,
    SpectacularSwaggerView,
)

from backend.settings.base import (
    APP_MODE,
    MEDIA_ROOT,
    MEDIA_URL,
    STATIC_ROOT,
    STATIC_URL,
    DjangoSettings,
)

urlpatterns = [
    path('admin/', admin.site.urls),

    path('api/v1/django-admin/users/', include('django_admin_users.urls')),
    path('api/v1/django-admin/model-docs/', include('django_admin_documentation.urls')),
    path('api/v1/django-admin/saved-queries/', include('django_admin_saved_queries.urls')),
    path('api/v1/django-admin/', include('django_admin.urls')),

    # API documentation 
    path('api/schema/', SpectacularAPIView.as_view(), name='schema'),
    # Optional UI:
    path('api/schema/docs/', SpectacularSwaggerView.as_view(url_name='schema'), name='swagger-ui'),
    path('api/schema/redoc/', SpectacularRedocView.as_view(url_name='schema'), name='redoc'),

    path('django-rq/', include('django_rq.urls'))
]

if APP_MODE == DjangoSettings.LOCAL:
    urlpatterns += static(STATIC_URL, document_root=STATIC_ROOT)
    urlpatterns += static(MEDIA_URL, document_root=MEDIA_ROOT)