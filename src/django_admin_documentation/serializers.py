from rest_framework import serializers

from .models import ModelDocumentation


class AdminModelDocumentationSerializer(serializers.ModelSerializer):
    class Meta:
        model = ModelDocumentation
        exclude = ['created_at', 'updated_at']