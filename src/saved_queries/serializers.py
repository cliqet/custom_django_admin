from rest_framework import serializers

from .models import SavedQueryBuilder


class QueryBuilderBodySerializer(serializers.Serializer):
    app_name = serializers.CharField()
    model_name = serializers.CharField()
    conditions = serializers.ListField(
        child=serializers.ListField(
            child=serializers.CharField(),  # Allow any type, but validate the first two as strings
            min_length=3,
            max_length=3
        )
    )
    orderings = serializers.ListField(child=serializers.CharField())
    query_limit = serializers.IntegerField(allow_null=True)

    def validate_conditions(self, value):
        for condition in value:
            if not isinstance(condition[0], str) or not isinstance(condition[1], str):
                raise serializers.ValidationError("The first two items in each condition must be strings.")
        return value
    

class RawQueryBodySerializer(serializers.Serializer):
    query = serializers.CharField()



class SavedQueryBuilderPostBodySerializer(serializers.Serializer):
    name = serializers.CharField()
    query = QueryBuilderBodySerializer()


class SavedQueryBuilderSerializer(serializers.ModelSerializer):
    class Meta:
        model = SavedQueryBuilder
        fields = ['id', 'name', 'query']