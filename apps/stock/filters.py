import django_filters

from apps.stock.models import Warehouse


class WarehouseFilter(django_filters.FilterSet):
    search = django_filters.CharFilter(lookup_expr='icontains', field_name='name')

    class Meta:
        model = Warehouse
        exclude = ('name',)
