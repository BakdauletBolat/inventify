from django.utils.decorators import method_decorator
from django.views.decorators.cache import cache_page
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework.generics import ListAPIView

from apps.category.filters import CategoryFilter
from apps.category.models import Category
from apps.category.serializers import CategorySerializer, CategoryTreeSerializer


class CategoryListAPIView(ListAPIView):
    queryset = Category.objects.all().order_by('id')
    serializer_class = CategorySerializer
    filter_backends = [DjangoFilterBackend]
    filterset_class = CategoryFilter


# Create your views here.

class CategoryTreeAPIView(ListAPIView):
    queryset = Category.objects.filter(parent__isnull=True).order_by('id')
    serializer_class = CategoryTreeSerializer
    filter_backends = [DjangoFilterBackend]
    filterset_class = CategoryFilter
    pagination_class = None

    @method_decorator(cache_page(60 * 60 * 24))  # кеширование на 1 день
    def dispatch(self, *args, **kwargs):
        return super().dispatch(*args, **kwargs)

    def get_queryset(self):
        return Category.objects.filter(parent__isnull=True).prefetch_related('children').order_by('id')
