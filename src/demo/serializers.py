from django_admin.serializers import BaseModelSerializer

from .models import Classification, Country, CountryProfile, DemoModel, Level, Type


class TypeSerializer(BaseModelSerializer):
    class Meta:
        model = Type
        fields = '__all__'


class ClassificationSerializer(BaseModelSerializer):
    class Meta:
        model = Classification
        fields = '__all__'


class DemoModelSerializer(BaseModelSerializer):
    class Meta:
        model = DemoModel
        fields = '__all__'


class LevelSerializer(BaseModelSerializer):
    class Meta:
        model = Level
        fields = '__all__'


class CountrySerializer(BaseModelSerializer):
    class Meta:
        model = Country
        fields = '__all__'


class CountryProfileSerializer(BaseModelSerializer):
    class Meta:
        model = CountryProfile
        fields = '__all__'
