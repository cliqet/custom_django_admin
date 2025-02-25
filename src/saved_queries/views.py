import logging
import re
from typing import Any

from django.core.cache import cache
from django.db import IntegrityError, connection
from django.db.models import QuerySet
from drf_spectacular.utils import OpenApiResponse, extend_schema
from rest_framework import status
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAdminUser
from rest_framework.response import Response

from django_admin.constants import CACHE_BY_DAY
from django_admin.permissions import IsSuperUser
from django_admin.util_models import get_model, get_model_fields_data
from django_admin.util_serializers import get_dynamic_serializer

from .constants import SAVED_QUERY_BUILDERS_CACHE_PREFIX
from .docs import (
    ADD_QUERY_BUILDER_DOC,
    CHANGE_QUERY_BUILDER_DOC,
    DELETE_QUERY_BUILDER_DOC,
    GET_ALL_QUERY_BUILDERS_DOC,
    QUERY_BUILDER_DOC,
    QUERY_BUILDER_ERROR_DOC,
)
from .models import SavedQueryBuilder
from .serializers import (
    QueryBuilderBodySerializer,
    RawQueryBodySerializer,
    SavedQueryBuilderPostBodySerializer,
    SavedQueryBuilderSerializer,
)
from .utils import (
    build_conditions_query,
    transform_conditions_query,
)

log = logging.getLogger(__name__)

@extend_schema(
    request=QueryBuilderBodySerializer,
    responses={
        status.HTTP_202_ACCEPTED: OpenApiResponse(
            description=QUERY_BUILDER_DOC
        ),
        status.HTTP_400_BAD_REQUEST: OpenApiResponse(
            description=QUERY_BUILDER_ERROR_DOC
        ),
    }
)
@api_view(['POST'])
@permission_classes([IsAdminUser])
def query_builder(request):
    try:
        body = request.data
        serialized_body = QueryBuilderBodySerializer(data=body)

        if serialized_body.is_valid():
            app_name: str = body.get('app_name')
            model_name: str = body.get('model_name')

            model = get_model(f'{app_name}.{model_name.lower()}')
            model_fields_data = get_model_fields_data(model)

            conditions: list[list[str | Any]] = body.get('conditions')
            if conditions:
                model_fields_data = get_model_fields_data(model)
                transformed_conditions = transform_conditions_query(conditions, model_fields_data)

                query = build_conditions_query(transformed_conditions)
                results: QuerySet = model.objects.filter(query)
            else:
                results = model.objects.all()

            orderings: list[str] = body.get('orderings')
            for order in orderings:
                results = results.order_by(order)

            query_limit = body.get('query_limit')
            if query_limit:
                results = results[:query_limit]

            model_serializer = get_dynamic_serializer(app_name, model)
            serialized_results = model_serializer(results, many=True).data

            return Response({
                'count': len(results),
                'fields': list(model_fields_data.keys()),
                'results': serialized_results
            }, status=status.HTTP_202_ACCEPTED)
        
        # If there are serialization errors
        error_messages = {}
        for field, errors in serialized_body.errors.items():
            error_messages[field] = [str(error) for error in errors]
        
        return Response({
            'count': 0,
            'fields': [],
            'results': [],
            'message': 'Invalid data',
            'validation_error': error_messages
        }, status=status.HTTP_400_BAD_REQUEST)
    except Exception as e:
        log.error(f'Error with query builder: {str(e)}')

        return Response({
            'count': 0,
            'fields': [],
            'results': [],
            'message': f'Error with query builder: {str(e)}'
        }, status=status.HTTP_400_BAD_REQUEST)
    

@extend_schema(
    request=RawQueryBodySerializer,
    responses={
        status.HTTP_202_ACCEPTED: OpenApiResponse(
            description=QUERY_BUILDER_DOC
        ),
        status.HTTP_400_BAD_REQUEST: OpenApiResponse(
            description=QUERY_BUILDER_ERROR_DOC
        ),
    }
)
@api_view(['POST'])
@permission_classes([IsAdminUser, IsSuperUser])
def raw_query(request):
    try:
        body = request.data
        serialized_body = RawQueryBodySerializer(data=body)

        if serialized_body.is_valid():
            query = body.get('query')

            # NOTE: Remove this check if you want no limitations to the query
            # =============================================================
            query_lower = query.lower().strip()
            if re.search(r'\b(update|delete|drop|truncate|insert)\b', query_lower):
                return Response({
                    'count': 0,
                    'fields': [],
                    'results': [],
                    'message': 'Query is not allowed'
                }, status=status.HTTP_400_BAD_REQUEST)
            # =============================================================

            with connection.cursor() as cursor:
                cursor.execute(query)  
                columns = [col[0] for col in cursor.description]
                
                results = cursor.fetchall()  

                # Format results as a list of dictionaries
                response_data = [
                    dict(zip(columns, row)) for row in results
                ]

            return Response({
                'count': len(results),
                'fields': columns,
                'results': response_data,
            }, status=status.HTTP_202_ACCEPTED)
        
        # If there are serialization errors
        error_messages = {}
        for field, errors in serialized_body.errors.items():
            error_messages[field] = [str(error) for error in errors]
        
        return Response({
            'count': 0,
            'fields': [],
            'results': [],
            'message': 'Invalid data',
            'validation_error': error_messages
        }, status=status.HTTP_400_BAD_REQUEST)
    except Exception as e:
        log.error(f'Error with query builder: {str(e)}')

        return Response({
            'count': 0,
            'fields': [],
            'results': [],
            'message': f'Error with query builder: {str(e)}'
        }, status=status.HTTP_400_BAD_REQUEST)

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


@extend_schema(
    responses={
        status.HTTP_202_ACCEPTED: OpenApiResponse(
            description=DELETE_QUERY_BUILDER_DOC
        ),
    }
)
@api_view(['DELETE'])
@permission_classes([IsSuperUser])
def delete_query_builder(request, id: int):
    try:
        saved_query = SavedQueryBuilder.objects.get(id=id)
        saved_query.delete()

        return Response({
            'message': f'Successfully deleted query with id {id}'
        }, status=status.HTTP_202_ACCEPTED)
    except SavedQueryBuilder.DoesNotExist as e:
        log.error(f'Failed to delete query builder: {str(e)}')

        return Response({
            'message': f'Query with id {id} does not exist'
        }, status=status.HTTP_404_NOT_FOUND)
    except Exception as e:
        log.error(f'Failed to delete query builder: {str(e)}')

        return Response({
            'message': 'Something went wrong'
        }, status=status.HTTP_400_BAD_REQUEST)