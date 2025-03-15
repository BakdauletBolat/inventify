import django_filters
from django_filters import OrderingFilter

from apps.order.enums import OrderStatusChoices
from apps.order.models import Order


class OrderFilter(django_filters.FilterSet):
    status = django_filters.ChoiceFilter(field_name="status", choices=OrderStatusChoices.choices, empty_label=None)

    sort = OrderingFilter(
        fields=(
            ('id', 'id'),
            ('created_at', 'created_at'),
            ('status', 'status')
        )
    )

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        if "status" not in self.data:
            self.queryset = self.queryset.exclude(status=OrderStatusChoices.DELETED.value)

    class Meta:
        model = Order
        fields = '__all__'
