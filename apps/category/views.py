from django.utils.decorators import method_decorator
from django.views.decorators.cache import cache_page
from django.db.models import Count, Prefetch
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework.generics import ListAPIView
from rest_framework.mixins import ListModelMixin, RetrieveModelMixin
from rest_framework.viewsets import GenericViewSet

from apps.category.filters import CategoryFilter
from apps.category.models import Category
from apps.category.serializers import CategorySerializer, CategoryTreeSerializer


class CategoryListAPIView(GenericViewSet, RetrieveModelMixin, ListModelMixin):
    serializer_class = CategorySerializer
    filter_backends = [DjangoFilterBackend]
    filterset_class = CategoryFilter

    def get_queryset(self):
        return (Category.objects
                .filter(status=Category.STATUS_ACTIVE)
                .annotate(products_count=Count('products'))
                .order_by('-products_count', '-id'))


class CategoryTreeAPIView(ListAPIView):
    queryset = Category.objects.filter(parent__isnull=True)
    serializer_class = CategoryTreeSerializer
    filter_backends = [DjangoFilterBackend]
    filterset_class = CategoryFilter
    pagination_class = None

    def dispatch(self, *args, **kwargs):
        return super().dispatch(*args, **kwargs)

    def get_queryset(self):
        """
            Возвращает дерево категорий с количеством продуктов в каждой категории.
        """
        child_qs = (Category.objects
                    .filter(status=Category.STATUS_ACTIVE)
                    .annotate(products_count=Count('products'))
                    .order_by('-products_count', '-id'))
        return (Category.objects
                .filter(parent__isnull=True, status=Category.STATUS_ACTIVE)
                .annotate(products_count=Count('products'))
                .prefetch_related(Prefetch('children', queryset=child_qs))
                .order_by('-products_count', '-id'))
