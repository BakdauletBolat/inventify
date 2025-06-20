import django_filters
from django_filters import OrderingFilter

from base.enums import StatusEnum
from users.models.User import User


class UserFilter(django_filters.FilterSet):
    status = django_filters.ChoiceFilter(field_name="status", choices=StatusEnum.choices, empty_label=None)
    phone = django_filters.CharFilter(lookup_expr='icontains', field_name="phone")

    class Meta:
        model = User
        fields = '__all__'

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
            self.queryset = self.queryset.filter(status=StatusEnum.ACTIVE.value)
