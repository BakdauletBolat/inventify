from django_filters.rest_framework import DjangoFilterBackend
from rest_framework.generics import ListAPIView

from apps.category.filters import CategoryFilter
from apps.category.models import Category
from apps.category.serializers import CategorySerializer


class CategoryListAPIView(ListAPIView):
    queryset = Category.objects.all().order_by('id')
    serializer_class = CategorySerializer
    filter_backends = [DjangoFilterBackend]
    filterset_class = CategoryFilter
# Create your views here.
