from django.contrib.postgres.search import TrigramSimilarity, SearchVector, SearchQuery, SearchRank
from django.db.models import Q
from django.db.models.functions import Greatest
from django.shortcuts import get_object_or_404
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

    def list(self, request):
        queryset = ShoppingList.objects.filter(user=request.user)

        paginator = self.pagination_class()
        page = paginator.paginate_queryset(queryset, request)
        if page is not None:
            serializer = serializers.ListSerializer(page, many=True)
            return paginator.get_paginated_response(serializer.data)

        serializer = serializers.ListSerializer(queryset, many=True)
        return Response(serializer.data)

    def create(self, request):
        serializer = serializers.ListSerializer(data=request.data)

        if serializer.is_valid():
            serializer.save(user=request.user)
            return Response(serializer.data, status=status.HTTP_201_CREATED)

        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def retrieve(self, request, slug=None):
        queryset = get_object_or_404(ShoppingList, slug=slug, user=request.user)
        serializer = serializers.ListSerializer(queryset)
        return Response(serializer.data)

    def partial_update(self, request, slug=None):
        queryset = get_object_or_404(ShoppingList, user=request.user, slug=slug)
        serializer = serializers.ListSerializer(queryset, data=request.data, partial=True)

        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_200_OK)

        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def destroy(self, request, slug=None):
        queryset = get_object_or_404(ShoppingList, user=request.user, slug=slug)
        queryset.delete()

        return Response(status=status.HTTP_204_NO_CONTENT)


class ItemViewSet(viewsets.ViewSet):
    permission_classes = (permissions.IsAuthenticated,)

    def create(self, request, slug=None):
        list_instance = get_object_or_404(ShoppingList, slug=slug, user=request.user)
        serializer = serializers.ItemSerializer(data=request.data)

        if serializer.is_valid():
            serializer.save(list=list_instance)
            return Response(serializer.data, status=status.HTTP_201_CREATED)

        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def partial_update(self, request, slug=None):
        queryset = get_object_or_404(Item, slug=slug)
        serializer = serializers.ItemSerializer(queryset, request.data, partial=True)

        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_200_OK)

        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def destroy(self, request, slug=None):
        queryset = get_object_or_404(Item, slug=slug)
        queryset.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)


class SearchView(APIView):
    permission_classes = (permissions.IsAuthenticated,)

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
