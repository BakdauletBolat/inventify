import django_filters

from apps.car.models.Model import ManufacturerType, ModelCar
from apps.car.models.Modification import Modification, Engine


class ModificationFilter(django_filters.FilterSet):
    class Meta:
        model = Modification
        fields = '__all__'


class ManufacturerFilter(django_filters.FilterSet):
    class Meta:
        model = ManufacturerType
        exclude = ('image',)


class ModelCarFilter(django_filters.FilterSet):
    class Meta:
        model = ModelCar
        fields = '__all__'


class EngineFilter(django_filters.FilterSet):
    class Meta:
        model = Engine
        fields = '__all__'
