from uuid import uuid4

from django.contrib.auth.models import (
    AbstractBaseUser,
    BaseUserManager,
    PermissionsMixin,
)
from django.core.validators import EmailValidator, RegexValidator
from django.db import models
from django.utils import timezone


def generate_user_id() -> str:
    return f'user_{uuid4()}'

class CustomUserManager(BaseUserManager):
    def _create_user(self, email, password, **extra_fields):
        if not email:
            raise ValueError('You have not provided an email address')
        
        email = self.normalize_email(email)
        user = self.model(email=email, **extra_fields)
        user.set_password(password)

        user.save(using=self._db)

        return user
    
    # override
    def create_user(self, email=None, password=None, **extra_fields):
        extra_fields.setdefault('is_active', False)
        extra_fields.setdefault('is_staff', False)
        extra_fields.setdefault('is_superuser', False)

        return self._create_user(email, password, **extra_fields)
    
    # override
    def create_superuser(self, email=None, password=None, **extra_fields):
        extra_fields.setdefault('is_active', True)
        extra_fields.setdefault('is_staff', True)
        extra_fields.setdefault('is_superuser', True)

        return self._create_user(email, password, **extra_fields)


class CustomUser(AbstractBaseUser, PermissionsMixin):
    serializer_classname = 'CustomUserDetailsSerializer'
    
    uid = models.CharField(
        max_length=255, 
        primary_key=True, 
        default=generate_user_id, 
        editable=False,
        verbose_name='UID'
    )
    email = models.EmailField(
        default='', 
        unique=True, 
        verbose_name='Email Address', 
        help_text='Enter a valid email address',
        validators=[EmailValidator(message='Please enter a valid email address')]
    )
    first_name = models.CharField(max_length=255, default='', verbose_name='First Name')
    last_name = models.CharField(max_length=255, default='', verbose_name='Last Name')
    password = models.CharField(
        validators=[
            RegexValidator(
                regex=r'^(?=.*\d).{8,}$',
                message='Password must be at least 8 characters long and contain at least one digit.'
            )
        ], 
        max_length=128,
        help_text='Must be at least 8 characters and must have at least 1 digit',
        verbose_name='Password'
    )
    created_at = models.DateTimeField(auto_now_add=True, verbose_name='Created At')
    updated_at = models.DateTimeField(auto_now=True, verbose_name='Updated At')

    is_active = models.BooleanField(default=False, blank=True, verbose_name='Is Active')
    is_superuser = models.BooleanField(default=False, blank=True, verbose_name='Is Superuser')
    is_staff = models.BooleanField(default=False, blank=True, verbose_name='Is Staff')

    date_joined = models.DateTimeField(default=timezone.now, blank=True, verbose_name='Date Joined')
    last_login = models.DateTimeField(blank=True, null=True, editable=False, verbose_name='Last Login')

    objects = CustomUserManager()

    USERNAME_FIELD = 'email'
    EMAIL_FIELD = 'email'
    REQUIRED_FIELDS = []

    class Meta:
        verbose_name = 'User'
        verbose_name_plural = 'Users'

    def __str__(self) -> str:
        return f'{self.email}'

    # override
    def get_full_name(self):
        if self.first_name and self.first_name:
            return f'{self.first_name} {self.last_name}'
        else:
            return self.email
    
    # override
    def get_short_name(self):
        return self.first_name or self.email.split('@')[0]
    
    def get_initials(self):
        first_initial = self.email[0]
        last_initial = self.email[1]
        if self.first_name:
            first_initial = self.first_name[0]
        if self.last_name:
            last_initial = self.last_name[0]
        return f'{first_initial.upper()} {last_initial.upper()}'

    # Override related names for groups and user permissions
    groups = models.ManyToManyField(
        'auth.Group',
        related_name='customuser_set',  # Change this to avoid clashes
        blank=True,
    )
    
    user_permissions = models.ManyToManyField(
        'auth.Permission',
        related_name='customuser_set',  # Change this to avoid clashes
        blank=True,
    )    
    

