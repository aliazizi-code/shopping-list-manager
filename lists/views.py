from django.contrib.postgres.search import TrigramSimilarity, SearchVector, SearchQuery, SearchRank
from django.db.models import Q
from django.db.models.functions import Greatest
from django.shortcuts import get_object_or_404
from drf_spectacular.utils import extend_schema
from rest_framework import permissions, status
from rest_framework import viewsets
from rest_framework.pagination import PageNumberPagination
from rest_framework.request import Request
from rest_framework.response import Response
from rest_framework.views import APIView

from lists import serializers
from lists.models import ShoppingList, Item


class ListPagination(PageNumberPagination):
    page_size = 5
    page_size_query_param = 'page_size'
    max_page_size = 100

    def get_paginated_response(self, data):
        return Response({
            'links': {
                'next': self.get_next_link(),
                'previous': self.get_previous_link()
            },
            'list_count': self.page.paginator.count,
            'results': data
        })


class ListViewSet(viewsets.ViewSet):
    permission_classes = (permissions.IsAuthenticated,)
    pagination_class = ListPagination

    @extend_schema(
        operation_id='listShoppingLists',
        request=None,
        responses={
            200: serializers.ListSerializer(many=True),
            401: 'Unauthorized - User is not authenticated',
        },
        summary='Retrieve a list of shopping lists',
        description='Returns a paginated list of shopping lists for the authenticated user.'
    )
    def list(self, request):
        queryset = ShoppingList.objects.filter(user=request.user)

        paginator = self.pagination_class()
        page = paginator.paginate_queryset(queryset, request)
        if page is not None:
            serializer = serializers.ListSerializer(page, many=True)
            return paginator.get_paginated_response(serializer.data)

        serializer = serializers.ListSerializer(queryset, many=True)
        return Response(serializer.data)

    @extend_schema(
        operation_id='createShoppingList',
        request=serializers.ListSerializer,
        responses={
            201: serializers.ListSerializer,
            400: 'Invalid Input data',
        },
        summary='Create a new shopping list',
        description='Creates a new shopping list for the authenticated user.'
    )
    def create(self, request):
        serializer = serializers.ListSerializer(data=request.data)

        if serializer.is_valid():
            serializer.save(user=request.user)
            return Response(serializer.data, status=status.HTTP_201_CREATED)

        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    @extend_schema(
        operation_id='retrieveShoppingList',
        request=None,
        responses={
            200: serializers.ListSerializer,
            404: 'Shopping list not found',
        },
        summary='Retrieve a specific shopping list',
        description='Returns the details of a shopping list identified by its slug.'
    )
    def retrieve(self, request, slug=None):
        queryset = get_object_or_404(ShoppingList, slug=slug, user=request.user)
        serializer = serializers.ListSerializer(queryset)
        return Response(serializer.data)

    @extend_schema(
        operation_id='partialUpdateShoppingList',
        request=serializers.ListSerializer,
        responses={
            200: serializers.ListSerializer,
            400: 'Invalid input data',
            404: 'Shopping list not found',
        },
        summary='Partially update a shopping list',
        description='Updates specific fields of a shopping list identified by its slug.'
    )
    def partial_update(self, request, slug=None):
        queryset = get_object_or_404(ShoppingList, user=request.user, slug=slug)
        serializer = serializers.ListSerializer(queryset, data=request.data, partial=True)

        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_200_OK)

        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    @extend_schema(
        operation_id='deleteShoppingList',
        request=None,
        responses={
            204: 'No Content - Shopping list deleted successfully',
            404: 'Shopping list not found',
        },
        summary='Delete a shopping list',
        description='Deletes a shopping list identified by its slug.'
    )
    def destroy(self, request, slug=None):
        queryset = get_object_or_404(ShoppingList, user=request.user, slug=slug)
        queryset.delete()

        return Response(status=status.HTTP_204_NO_CONTENT)


class ItemViewSet(viewsets.ViewSet):
    permission_classes = (permissions.IsAuthenticated,)

    @extend_schema(
        operation_id='createItem',
        request=serializers.ItemSerializer,
        responses={
            201: serializers.ItemSerializer,
            400: 'Invalid input data',
        },
        summary='Create a new item',
        description='Creates a new item for the specified shopping list.'
    )
    def create(self, request, slug=None):
        list_instance = get_object_or_404(ShoppingList, slug=slug, user=request.user)
        serializer = serializers.ItemSerializer(data=request.data)

        if serializer.is_valid():
            serializer.save(list=list_instance)
            return Response(serializer.data, status=status.HTTP_201_CREATED)

        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    @extend_schema(
        operation_id='partialUpdateItem',
        request=serializers.ItemSerializer,
        responses={
            200: serializers.ItemSerializer,
            400: 'Invalid input data',
            404: 'Item not found',
        },
        summary='Partially update an item',
        description='Updates specific fields of an item identified by its slug.'
    )
    def partial_update(self, request, slug=None):
        queryset = get_object_or_404(Item, slug=slug)
        serializer = serializers.ItemSerializer(queryset, request.data, partial=True)

        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_200_OK)

        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    @extend_schema(
        operation_id='deleteItem',
        request=None,
        responses={
            204: 'No Content - Item deleted successfully',
            404: 'Item not found',
        },
        summary='Delete an item',
        description='Deletes an item identified by its slug.'
    )
    def destroy(self, request, slug=None):
        queryset = get_object_or_404(Item, slug=slug)
        queryset.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)


class SearchView(APIView):
    permission_classes = (permissions.IsAuthenticated,)

    @extend_schema(
        operation_id='searchShoppingLists',
        request=serializers.ListSerializer,
        responses={
            200: {
                'type': 'array',
                'items': {
                    'type': 'object',
                    'properties': {
                        'name': {'type': 'string'},
                        'slug': {'type': 'string'},
                    },
                },
            },
            401: 'Unauthorized - User is not authenticated',
        },
        summary='Search shopping lists',
        description='Returns a list of shopping lists that match the search term based on name, description, and item names.'
    )
    def get(self, request: Request):
        search_term = request.query_params.get('search', '')

        search_vector = SearchVector('name', 'description', 'items__name')
        search_query = SearchQuery(search_term)
        search_rank = SearchRank(search_vector, search_query)

        similarity_filter = Greatest(
            TrigramSimilarity('name', search_term),
            TrigramSimilarity('description', search_term),
            TrigramSimilarity('items__name', search_term)
        )

        queryset = (
            ShoppingList.objects
            .annotate(rank=search_rank, similarity=similarity_filter)
            .filter(Q(user=request.user), Q(rank__gt=0.3) | Q(similarity__gt=0.3))
            .values('name', 'slug')
            .distinct()
            .order_by('-rank', '-similarity')
        )

        return Response(list(queryset))
