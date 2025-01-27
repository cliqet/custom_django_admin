from django.urls import path

from .views import get_model_docs

urlpatterns = [
    path('', get_model_docs, name='get_model_docs'),
]
