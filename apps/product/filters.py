import django_filters

from apps.product.models import Product


class ProductFilters(django_filters.FilterSet):
    price = django_filters.RangeFilter(field_name='price__cost')
    year_start = django_filters.NumberFilter(field_name='modification__modelCar__startDate__year', lookup_expr='gte')
    year_end = django_filters.NumberFilter(field_name='modification__modelCar__startDate__year', lookup_expr='lte')
    capacity = django_filters.RangeFilter(field_name='modification__capacity')
    body_type = django_filters.BaseInFilter(field_name='modification__bodyType')
    fuel_type = django_filters.BaseInFilter(field_name='modification__fuelType')
    gear_type = django_filters.BaseInFilter(field_name='modification__gearType')
    manufacturer = django_filters.BaseInFilter(field_name='modification__modelCar__manufacturer')

    class Meta:
        model = Product
        fields = ('__all__')
