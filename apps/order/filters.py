import django_filters

from apps.order.models import Order


class OrderFilter(django_filters.FilterSet):

    class Meta:
        model = Order
        fields = '__all__'

