from django.contrib.auth.models import Permission
from django.core.validators import (
    EmailValidator,
    MaxValueValidator,
    MinValueValidator,
    RegexValidator,
)
from django.db import models

from django_admin.models import BaseModel, HTMLField
from django_admin.util_models import build_filefield_helptext


class Type(BaseModel):
    admin_serializer_classname = 'AdminTypeSerializer'

    name = models.CharField(max_length=100, verbose_name='Name')

    def __str__(self):
        return self.name
    

class Classification(BaseModel):
    admin_serializer_classname = 'AdminClassificationSerializer'

    name = models.CharField(max_length=100, verbose_name='Name')

    def __str__(self):
        return self.name


class DemoModel(BaseModel):
    admin_serializer_classname = 'AdminDemoModelSerializer'

    class ColorChoices(models.TextChoices):
        BLUE = ('Blue', 'Blue')
        RED = ('Red', 'Red')
    type = models.ForeignKey(Type, on_delete=models.CASCADE, verbose_name='Type')
    color = models.CharField(
        verbose_name='Color', 
        choices=ColorChoices.choices, 
        default=ColorChoices.BLUE,
        max_length=10
    )
    name = models.CharField(max_length=100, verbose_name='Name', unique=True)
    email = models.EmailField(
        validators=[EmailValidator(message='Please enter a valid email address')],
        help_text='Please enter a valid email address',
        verbose_name='Email'
    )
    ordering = models.PositiveIntegerField(verbose_name='Ordering', default=0)
    range_number = models.PositiveSmallIntegerField(
        verbose_name='Range Number',
        default=5,
        help_text='Enter a number from 5 to 10',
        validators=[
            MinValueValidator(limit_value=5, message='Min is 5'),
            MaxValueValidator(limit_value=10, message='Max is 10'),
        ]
    )
    amount = models.DecimalField(
        default=0.0, 
        decimal_places=2, 
        max_digits=10, 
        verbose_name='Amount',
        help_text='Max of 10 digits with format: 12345678.90',
        validators=[
            RegexValidator(regex=r'^\d{1,8}(\.\d{0,2})?$', message='Enter a valid amount (up to 8 digits before the decimal and 2 digits')
        ]
    )
    comment = models.TextField(verbose_name='Comment')
    is_active = models.BooleanField(verbose_name='Is Active', default=True)
    date = models.DateField(verbose_name='Date')
    time = models.TimeField(verbose_name='Time')
    last_log = models.DateTimeField(verbose_name='Last Log')
    classification = models.ManyToManyField(Classification, verbose_name='Classification')
    permissions = models.ManyToManyField(Permission, verbose_name='Permissions')
    file = models.FileField(verbose_name='File', help_text=build_filefield_helptext())
    image = models.ImageField(
        verbose_name='Image',
        help_text=build_filefield_helptext(['.jpg', '.jpeg', '.png'], 2)
    )
    metadata = models.JSONField(verbose_name='Metadata')
    html = HTMLField(verbose_name='HTML', help_text='Enter html')


    def __str__(self):
        return self.name
    

class Level(BaseModel):
    admin_serializer_classname = 'AdminLevelSerializer'

    name = models.CharField(max_length=10, help_text='Enter level')

    def __str__(self):
        return self.name
    

class Country(BaseModel):
    admin_serializer_classname = 'AdminCountrySerializer'

    class Meta:
        verbose_name_plural = 'Countries'
    name = models.CharField(max_length=50, help_text='Enter country')

    def __str__(self):
        return self.name
    

class CountryProfile(BaseModel):
    admin_serializer_classname = 'AdminCountryProfileSerializer'

    country = models.OneToOneField(Country, on_delete=models.CASCADE, help_text='Select country')
    level = models.ForeignKey(Level, on_delete=models.CASCADE, help_text='Select level')
    type = models.ForeignKey(Type, on_delete=models.CASCADE, help_text='Select type')
    area = models.PositiveIntegerField(help_text='Enter area number')

    def __str__(self):
        return self.country.name
    

