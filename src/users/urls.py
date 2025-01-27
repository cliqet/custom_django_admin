from django.urls import path

from .views import (
    CustomTokenObtainPairView,
    get_all_users,
    get_user_detail,
    get_user_permissions,
    logout,
)

urlpatterns = [
    path('login', CustomTokenObtainPairView.as_view(), name='login'),
    path('logout', logout, name='logout'),
    path('permissions/<str:uid>', get_user_permissions, name='get_user_permissions'),
    path('<str:uid>', get_user_detail, name='get_user_detail'),
    path('', get_all_users, name='get_all_users'),
]
