from django_admin.serializers import AdminBaseModelSerializer

from .models import Classification, Country, CountryProfile, DemoModel, Level, Type


class AdminTypeSerializer(AdminBaseModelSerializer):
    class Meta:
        model = Type
        fields = '__all__'


class AdminClassificationSerializer(AdminBaseModelSerializer):
    class Meta:
        model = Classification
        fields = '__all__'


class AdminDemoModelSerializer(AdminBaseModelSerializer):
    class Meta:
        model = DemoModel
        fields = '__all__'


class AdminLevelSerializer(AdminBaseModelSerializer):
    class Meta:
        model = Level
        fields = '__all__'


class AdminCountrySerializer(AdminBaseModelSerializer):
    class Meta:
        model = Country
        fields = '__all__'


class AdminCountryProfileSerializer(AdminBaseModelSerializer):
    class Meta:
        model = CountryProfile
        fields = '__all__'
