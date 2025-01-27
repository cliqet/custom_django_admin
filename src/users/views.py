import logging

from drf_spectacular.utils import OpenApiResponse, extend_schema
from rest_framework import status
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAdminUser
from rest_framework.response import Response
from rest_framework_simplejwt.views import (
    TokenObtainPairView,
    TokenRefreshView,
)

from backend.settings.base import APP_MODE, DjangoSettings
from django_admin.serializers import PermissionSerializer

from .docs import (
    GET_ALL_USERS_DOC,
    GET_USER_DETAIL_DOC,
    GET_USER_PERMISSIONS_DOC,
    LOGIN_DOC,
    LOGOUT_DOC,
)
from .models import CustomUser
from .serializers import CustomUserDetailsSerializer, CustomUserListSerializer
from .utils import get_user_unique_permissions, organize_permissions

log = logging.getLogger(__name__)

@extend_schema(
    responses={
        status.HTTP_200_OK: OpenApiResponse(
            response=CustomUserListSerializer,
            description=GET_ALL_USERS_DOC
        ),
    }
)
@api_view(['GET'])
@permission_classes([IsAdminUser])
def get_all_users(request):
    users = CustomUser.objects.all()

    return Response({
        'users': CustomUserListSerializer(users, many=True).data
    }, status=status.HTTP_200_OK)


@extend_schema(
    responses={
        status.HTTP_200_OK: OpenApiResponse(
            response=CustomUserDetailsSerializer,
            description=GET_USER_DETAIL_DOC
        ),
        status.HTTP_404_NOT_FOUND: OpenApiResponse(
            response=None,
            description='User not found. Returns None for user'
        ),
    }
)
@api_view(['GET'])
@permission_classes([IsAdminUser])
def get_user_detail(request, uid: str):
    try:
        user = CustomUser.objects.get(uid=uid)

        return Response({
            'user': CustomUserDetailsSerializer(user).data
        }, status=status.HTTP_200_OK)
    except CustomUser.DoesNotExist:
        return Response({
            'user': None
        }, status=status.HTTP_404_NOT_FOUND)


@extend_schema(
    responses={
        status.HTTP_200_OK: OpenApiResponse(
            description=GET_USER_PERMISSIONS_DOC
        ),
        status.HTTP_404_NOT_FOUND: OpenApiResponse(
            description='If user does not exist'
        ),
    }
)
@api_view(['GET'])
@permission_classes([IsAdminUser])
def get_user_permissions(request, uid: str):
    try:
        user = CustomUser.objects.get(uid=uid)
        unique_permissions = get_user_unique_permissions(user)
        serialized_permissions = PermissionSerializer(unique_permissions, many=True).data

        return Response({
            'permissions': organize_permissions(serialized_permissions, request.user)
        }, status=status.HTTP_200_OK)
    except CustomUser.DoesNotExist:
        return Response({
            'message': 'No record found'
        }, status=status.HTTP_404_NOT_FOUND)
    

@extend_schema(
    responses={
        status.HTTP_200_OK: OpenApiResponse(
            description=LOGIN_DOC
        ),
    }
)
class CustomTokenObtainPairView(TokenObtainPairView):
    def post(self, request, *args, **kwargs):
        log.info(f"Login attempt for user: {request.data.get('email')}")

        # Call the parent class's post method to handle token creation
        response = super().post(request, *args, **kwargs)

        is_secure_cookie = APP_MODE != DjangoSettings.LOCAL

        # Set the refresh token in a secure cookie
        refresh_token = response.data.get('refresh')
        response.set_cookie(
            key='app.refresh_token',
            value=refresh_token,
            httponly=True,  # Prevent JavaScript access
            secure=is_secure_cookie,    # Only send cookie over HTTPS
            samesite='Lax', # Adjust as necessary for your use case
        )

        response.data.pop('refresh', None)

        return response
    

@extend_schema(
    responses={
        status.HTTP_202_ACCEPTED: OpenApiResponse(
            description=LOGOUT_DOC
        ),
    }
)
@api_view(['POST'])
@permission_classes([IsAdminUser])
def logout(request):
    response = Response({
        'message': 'Logged out successfully.'
    }, status=status.HTTP_202_ACCEPTED)
    response.delete_cookie('app.refresh_token')  # Remove the refresh token cookie
    return response