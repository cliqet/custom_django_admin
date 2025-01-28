from uuid import uuid4

from rest_framework import serializers
from rest_framework_simplejwt.serializers import TokenObtainPairSerializer

from django_admin.serializers import BaseModelSerializer

from .models import CustomUser


class CustomUserListSerializer(BaseModelSerializer):
    class Meta:
        model = CustomUser
        fields = [
            'uid', 'email', 'first_name', 'last_name', 'is_active', 'is_staff', 
            'is_superuser'
        ]


class CustomUserDetailsSerializer(BaseModelSerializer):
    class Meta:
        model = CustomUser
        exclude = ['password']


class UserObtainPairSerializer(TokenObtainPairSerializer):
    """ Customize claims for token """
    @classmethod
    def get_token(cls, user: CustomUser):
        token = super().get_token(user)

        # Add custom claims
        token['uid'] = user.uid
        token['first_name'] = user.first_name
        token['last_name'] = user.last_name
        token['email'] = user.email
        token['is_superuser'] = user.is_superuser
        token['is_staff'] = user.is_staff
        token['is_active'] = user.is_active
        token['initials'] = user.get_initials()
        token['session_id'] = str(uuid4())

        return token
    

class ResetPasswordViaLinkBodySerializer(serializers.Serializer):
    password = serializers.CharField()