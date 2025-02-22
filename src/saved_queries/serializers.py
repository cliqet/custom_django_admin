from rest_framework import serializers

from django_admin.serializers import QueryBuilderBodySerializer

from .models import SavedQueryBuilder


class SavedQueryBuilderPostBodySerializer(serializers.Serializer):
    name = serializers.CharField()
    query = QueryBuilderBodySerializer()


class SavedQueryBuilderSerializer(serializers.ModelSerializer):
    class Meta:
        model = SavedQueryBuilder
        fields = ['id', 'name', 'query']