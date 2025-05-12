from django.core.cache import cache
from drf_spectacular.utils import OpenApiResponse, extend_schema
from rest_framework import status
from rest_framework.decorators import api_view, permission_classes
from rest_framework.response import Response

from django_admin.data_transform import transform_dict_to_camel_case
from django_admin.permissions import IsActiveAdminUser

from .docs import GET_MODEL_DOCS_DOC
from .models import ModelDocumentation
from .serializers import AdminModelDocumentationSerializer


@extend_schema(
    responses={
        status.HTTP_200_OK: OpenApiResponse(
            response=AdminModelDocumentationSerializer,
            description=GET_MODEL_DOCS_DOC
        ),
    }
)
@api_view(['GET'])
@permission_classes([IsActiveAdminUser])
def get_model_docs(request):
    cache_key = ModelDocumentation.CACHE_KEY_PREFIX
    cached_data = cache.get(cache_key)

    if cached_data:
        return Response(cached_data, status=status.HTTP_200_OK)
    
    docs = ModelDocumentation.objects.all()
    serialized_docs = transform_dict_to_camel_case({
        'docs': AdminModelDocumentationSerializer(docs, many=True).data
    })

    cache.set(cache_key, serialized_docs)

    return Response(serialized_docs, status=status.HTTP_200_OK)
