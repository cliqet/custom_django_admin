from django.urls import path

from .views import add_query_builder, get_all_query_builders

urlpatterns = [
    path('query-builder/add', add_query_builder, name='add_query_builder'),
    path('query-builder', get_all_query_builders, name='get_all_query_builders'),
]
