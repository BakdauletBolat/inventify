import django_filters

from handbook.models import City


class CityFilterSet(django_filters.FilterSet):
    class Meta:
        model = City
        fields = '__all__'
