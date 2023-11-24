from django_filters import filterset

from apps.category.models import Category


class CategoryFilter(filterset.FilterSet):
    class Meta:
        model = Category
        fields = '__all__'
