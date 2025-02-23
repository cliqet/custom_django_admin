import logging

from django.core.cache import cache
from django.db import IntegrityError
from drf_spectacular.utils import OpenApiResponse, extend_schema
from rest_framework import status
from rest_framework.decorators import api_view, permission_classes
from rest_framework.response import Response

from django_admin.constants import CACHE_BY_DAY
from django_admin.permissions import IsSuperUser

from .constants import SAVED_QUERY_BUILDERS_CACHE_PREFIX
from .docs import (
    ADD_QUERY_BUILDER_DOC,
    CHANGE_QUERY_BUILDER_DOC,
    GET_ALL_QUERY_BUILDERS_DOC,
)
from .models import SavedQueryBuilder
from .serializers import (
    SavedQueryBuilderPostBodySerializer,
    SavedQueryBuilderSerializer,
)

log = logging.getLogger(__name__)

@extend_schema(
    responses={
        status.HTTP_200_OK: OpenApiResponse(
            response=SavedQueryBuilderSerializer,
            description=GET_ALL_QUERY_BUILDERS_DOC
        ),
    }
)
@api_view(['GET'])
@permission_classes([IsSuperUser])
def get_all_query_builders(request):
    cached_data = cache.get(SAVED_QUERY_BUILDERS_CACHE_PREFIX)

    if cached_data:
        return Response({
            'queries': cached_data
        }, status=status.HTTP_200_OK)
    
    queries = SavedQueryBuilder.objects.all()
    serialized_queries = SavedQueryBuilderSerializer(queries, many=True).data

    cache.set(SAVED_QUERY_BUILDERS_CACHE_PREFIX, serialized_queries, CACHE_BY_DAY)

    return Response({
        'queries': serialized_queries
    }, status=status.HTTP_200_OK)


@extend_schema(
    request=SavedQueryBuilderPostBodySerializer,
    responses={
        status.HTTP_201_CREATED: OpenApiResponse(
            response=SavedQueryBuilderSerializer,
            description=ADD_QUERY_BUILDER_DOC
        ),
    }
)
@api_view(['POST'])
@permission_classes([IsSuperUser])
def add_query_builder(request):
    try:
        body = request.data
        serialized_body = SavedQueryBuilderPostBodySerializer(data=body)
        error_messages = {}

        if serialized_body.is_valid():
            SavedQueryBuilder.objects.create(**body)

            return Response({
                'message': f'Successfully added query {body.get("name")}'
            }, status=status.HTTP_201_CREATED)
        else:
            # If there are serialization errors
            for field, errors in serialized_body.errors.items():
                error_messages[field] = [str(error) for error in errors]

            log.error(f'Serialization error: {error_messages}')
        
            return Response({
                'message': 'Invalid data',
                'validation_error': error_messages
            }, status=status.HTTP_400_BAD_REQUEST)
    except IntegrityError as e:
        log.error(f'Failed to save query builder: {str(e)}')

        return Response({
            'message': f'A record with {body.get("name")} already exists'
        }, status=status.HTTP_400_BAD_REQUEST)
    except Exception as e:
        log.error(f'Failed to save query builder: {str(e)}')

        return Response({
            'message': 'Something went wrong'
        }, status=status.HTTP_400_BAD_REQUEST)
    

@extend_schema(
    request=SavedQueryBuilderPostBodySerializer,
    responses={
        status.HTTP_201_CREATED: OpenApiResponse(
            response=SavedQueryBuilderSerializer,
            description=CHANGE_QUERY_BUILDER_DOC
        ),
    }
)
@api_view(['POST'])
@permission_classes([IsSuperUser])
def change_query_builder(request, id: int):
    try:
        body = request.data
        serialized_body = SavedQueryBuilderPostBodySerializer(data=body)
        error_messages = {}

        if serialized_body.is_valid():
            saved_query = SavedQueryBuilder.objects.get(id=id)
            saved_query.name = body.get('name')
            saved_query.query = body.get('query')
            saved_query.save()

            return Response({
                'message': f'Successfully changed query with id {id}'
            }, status=status.HTTP_201_CREATED)
        else:
            # If there are serialization errors
            for field, errors in serialized_body.errors.items():
                error_messages[field] = [str(error) for error in errors]

            log.error(f'Serialization error: {error_messages}')
        
            return Response({
                'message': 'Invalid request',
                'validation_error': error_messages
            }, status=status.HTTP_400_BAD_REQUEST)
    except IntegrityError as e:
        log.error(f'Failed to change query builder: {str(e)}')

        return Response({
            'message': f'A record with {body.get("name")} already exists'
        }, status=status.HTTP_400_BAD_REQUEST)
    except SavedQueryBuilder.DoesNotExist as e:
        log.error(f'Failed to change query builder: {str(e)}')

        return Response({
            'message': f'Query with id {id} does not exist'
        }, status=status.HTTP_404_NOT_FOUND)
    except Exception as e:
        log.error(f'Failed to change query builder: {str(e)}')

        return Response({
            'message': 'Something went wrong'
        }, status=status.HTTP_400_BAD_REQUEST)
