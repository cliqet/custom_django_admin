import logging
from datetime import datetime, timedelta

from django.contrib.auth.tokens import default_token_generator
from django.utils.encoding import force_bytes
from django.utils.http import urlsafe_base64_decode, urlsafe_base64_encode
from drf_spectacular.utils import OpenApiResponse, extend_schema
from rest_framework import status
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAdminUser
from rest_framework.response import Response
from rest_framework_simplejwt.token_blacklist.models import BlacklistedToken
from rest_framework_simplejwt.tokens import RefreshToken
from rest_framework_simplejwt.views import (
    TokenObtainPairView,
    TokenRefreshView,
)

from backend.settings.base import (
    APP_MODE,
    DOMAIN,
    ENV,
    PROTOCOL,
    UI_DOMAIN,
    DjangoSettings,
)
from django_admin.serializers import AdminPermissionSerializer
from services.email_service import send_email
from services.queue_service import enqueue

from .docs import (
    GET_ALL_USERS_DOC,
    GET_USER_DETAIL_DOC,
    GET_USER_PERMISSIONS_DOC,
    LOGIN_DOC,
    LOGOUT_DOC,
    REFRESH_TOKEN_DOC,
    RESET_PASSWORD_VIA_LINK_DOC,
    SEND_PASSWORD_RESET_LINK_DOC,
    VERIFY_PASSWORD_RESET_LINK_DOC,
)
from .models import CustomUser
from .serializers import (
    AdminCustomUserDetailsSerializer,
    AdminCustomUserListSerializer,
    AdminResetPasswordViaLinkBodySerializer,
)
from .utils import get_user_unique_permissions, organize_permissions

log = logging.getLogger(__name__)

@extend_schema(
    responses={
        status.HTTP_200_OK: OpenApiResponse(
            response=AdminCustomUserListSerializer,
            description=GET_ALL_USERS_DOC
        ),
    }
)
@api_view(['GET'])
@permission_classes([IsAdminUser])
def get_all_users(request):
    users = CustomUser.objects.all()

    return Response({
        'users': AdminCustomUserListSerializer(users, many=True).data
    }, status=status.HTTP_200_OK)


@extend_schema(
    responses={
        status.HTTP_200_OK: OpenApiResponse(
            response=AdminCustomUserDetailsSerializer,
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
            'user': AdminCustomUserDetailsSerializer(user).data
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
        serialized_permissions = AdminPermissionSerializer(unique_permissions, many=True).data

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
    """
        Admin's login view
    """
    def post(self, request, *args, **kwargs):
        log.info(f"Login attempt for user: {request.data.get('email')}")

        # Call the parent class's post method to handle token creation
        response = super().post(request, *args, **kwargs)

        is_secure_cookie = APP_MODE != DjangoSettings.LOCAL

        cookie_expiration = datetime.now() + timedelta(
            days=ENV.application.jwt_refresh_token_life
        )

        # Set the refresh token in a secure cookie
        refresh_token = response.data.get('refresh')
        response.set_cookie(
            key='app.refresh_token',
            value=refresh_token,
            httponly=True,  # Prevent JavaScript access
            secure=is_secure_cookie,    # Only send cookie over HTTPS
            samesite='Lax', # Adjust as necessary for your use case
            path='/',
            domain=DOMAIN,
            expires=cookie_expiration,
        )

        response.data.pop('refresh', None)

        return response


@extend_schema(
    responses={
        status.HTTP_200_OK: OpenApiResponse(description=REFRESH_TOKEN_DOC),
    }
)
class CustomTokenRefreshView(TokenRefreshView):
    def post(self, request, *args, **kwargs):
        refresh_token_from_cookie = request.COOKIES.get('refresh_token')

        # If the cookie is missing, return an error
        if not refresh_token_from_cookie:
            return Response(
                {
                    'message': 'Invalid request',
                    'error': 'Refresh token is missing',
                },
                status=status.HTTP_401_UNAUTHORIZED,
            )

        try:
            # Decode the refresh token (this validates the token such as expiry, signature, ...)
            refresh_token = RefreshToken(refresh_token_from_cookie)

            # Ensure the token is a refresh token
            if refresh_token.payload.get('token_type') != 'refresh':
                return Response(
                    {'error': 'Invalid token type'}, status=status.HTTP_401_UNAUTHORIZED
                )

            if BlacklistedToken.objects.filter(
                token__token=refresh_token_from_cookie
            ).exists():
                return Response(
                    {'error': 'Token is blacklisted'},
                    status=status.HTTP_401_UNAUTHORIZED,
                )

            # Extract the user ID from the payload
            user_id = refresh_token.payload.get('user_id')
            user = CustomUser.objects.get(uid=user_id)

            # Create new access and refresh tokens
            new_access_token = str(refresh_token.access_token)
            new_refresh_token = str(RefreshToken.for_user(user))
        except Exception as e:
            log.error(f'Error decoding refresh token: {str(e)}')

            return Response(
                {'error': 'Invalid refresh token'}, status=status.HTTP_401_UNAUTHORIZED
            )

        # Prepare the response
        response = Response(
            {
                'access': new_access_token,
            }
        )

        is_secure_cookie = APP_MODE != DjangoSettings.LOCAL

        cookie_expiration = datetime.now() + timedelta(
            days=ENV.application.jwt_refresh_token_life
        )

        # Set the new refresh token in a secure cookie
        response.set_cookie(
            key='refresh_token',
            value=new_refresh_token,
            httponly=True,
            secure=is_secure_cookie,
            samesite='Lax',
            domain=DOMAIN,
            path='/',
            expires=cookie_expiration,
        )

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

@extend_schema(
    responses={
        status.HTTP_200_OK: OpenApiResponse(
            description=SEND_PASSWORD_RESET_LINK_DOC
        ),
    }
)
@api_view(['GET'])
@permission_classes([IsAdminUser])
def send_password_reset_link(request, uid):
    try:
        user = CustomUser.objects.get(uid=uid)
        uidb64 = urlsafe_base64_encode(force_bytes(user.pk))
        token = default_token_generator.make_token(user)
        link = f'{PROTOCOL}://{UI_DOMAIN}/users/reset/{uidb64}/{token}'

        subject = 'Password Reset Link'

        enqueue(
            send_email,
            [user.email],
            subject,
            email_template = 'email/reset-password.html',
            template_context={
                'firstname': user.first_name,
                'link': link,
            }
        )

        return Response({
            'success': True,
            'message': 'Password reset link has been sent to the email of the user'
        }, status=status.HTTP_200_OK)
    except CustomUser.DoesNotExist as e:
        log.error(f'Password reset error for {uid}: {str(e)}')

        return Response({
            'success': False,
            'message': 'User does not exist'
        }, status=status.HTTP_404_NOT_FOUND)
    except Exception:
        log.error(f'Password reset error for {uid}: {str(e)}')

        return Response({
            'success': False,
            'message': 'Something went wrong.'
        }, status=status.HTTP_400_BAD_REQUEST)
    

@extend_schema(
    responses={
        status.HTTP_200_OK: OpenApiResponse(
            description=VERIFY_PASSWORD_RESET_LINK_DOC
        ),
    }
)
@api_view(['GET'])
def verify_password_reset_link(request, uidb64, token):
    try:
        # Decode the uid
        uid = urlsafe_base64_decode(uidb64).decode()
        user = CustomUser.objects.get(pk=uid)
        
        # Check if the token is valid
        if default_token_generator.check_token(user, token):
            return Response({
                'valid': True, 'message': 'Token is valid.'
            }, status=status.HTTP_200_OK)
        else:
            return Response({
                'valid': False, 'message': 'Token is invalid or has expired.'
            }, status=status.HTTP_400_BAD_REQUEST)
    except Exception as e:
        log.error(f'Error verifying password reset link: {str(e)}')

        return Response({
            'valid': False, 'message': 'Invalid UID.'
        }, status=status.HTTP_400_BAD_REQUEST)

@extend_schema(
    responses={
        status.HTTP_201_CREATED: OpenApiResponse(
            description=RESET_PASSWORD_VIA_LINK_DOC
        ),
    }
)
@api_view(['POST'])
def reset_password_via_link(request, uidb64, token):
    try:
        body = request.data
        serialized_body = AdminResetPasswordViaLinkBodySerializer(data=body)
        if not serialized_body.is_valid():
            return Response({
                'success': False, 'message': 'Invalid request'
            }, status=status.HTTP_400_BAD_REQUEST)

        # Decode the uid
        uid = urlsafe_base64_decode(uidb64).decode()
        user = CustomUser.objects.get(pk=uid)
        
        # Check if the token is valid
        if default_token_generator.check_token(user, token):
            user.set_password(body.get('password'))
            user.save()

            return Response({
                'success': True, 'message': 'Successfully updated password'
            }, status=status.HTTP_201_CREATED)
        else:
            return Response({
                'success': False, 'message': 'Token is invalid or has expired.'
            }, status=status.HTTP_400_BAD_REQUEST)
    except Exception as e:
        log.error(f'Error resetting password via link: {str(e)}')

        return Response({
            'success': False, 'message': 'Invalid request'
        }, status=status.HTTP_400_BAD_REQUEST)