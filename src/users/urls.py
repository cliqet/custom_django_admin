from django.urls import path

from .views import (
    CustomTokenObtainPairView,
    get_all_users,
    get_user_detail,
    get_user_permissions,
    logout,
    reset_password_via_link,
    send_password_reset_link,
    verify_password_reset_link,
)

urlpatterns = [
    # This is for admin users only. DO NOT USE for website users if you have a 
    # customer facing website. 
    path('login', CustomTokenObtainPairView.as_view(), name='login'),
    path('logout', logout, name='logout'),
    path('send-password-reset-link/<str:uid>', send_password_reset_link, name='send_password_reset_link'),
    path('verify-password-reset-link/<str:uidb64>/<str:token>', verify_password_reset_link, name='verify_password_reset_link'),
    path('reset-password-via-link/<str:uidb64>/<str:token>', reset_password_via_link, name='reset_password_via_link'),
    path('permissions/<str:uid>', get_user_permissions, name='get_user_permissions'),
    path('<str:uid>', get_user_detail, name='get_user_detail'),
    path('', get_all_users, name='get_all_users'),
]
