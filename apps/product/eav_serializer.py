from django.db.models import F
from drf_yasg.utils import swagger_auto_schema
from eav.models import Attribute
from rest_framework import serializers

from apps.car.models.Model import ModelCar
from apps.car.serializers import ModelCarSerializer


class ProductEAVSerializer(serializers.Serializer):

    def to_representation(self, instance):

        # Создаем словарь для хранения значений атрибутов
        result = {}

        for value_obj in instance.eav_values.all().annotate(attr_name=F('attribute__name'),
                                                            attr_type=F('attribute__datatype')):
            value = value_obj.value
            if value is None:
                continue

            if value_obj.attr_type == Attribute.TYPE_OBJECT:
                if value is not None:
                    value = ModelCarSerializer(value).data
                    # value.pop('_state') # если требуется удалить '_state', раскомментируйте эту строку
            elif value_obj.attr_type == Attribute.TYPE_ENUM:
                value = getattr(value, 'value', None) if getattr(value, 'value', None) is not None else value

            result[value_obj.attr_name] = value

        return result

    def to_internal_value(self, data):
        validated_data = {}
        for attribute_name, value in data.items():
            attribute = Attribute.objects.get(name=attribute_name)

            # Если атрибут - enum, обрабатываем его по-особенному
            if attribute.datatype == Attribute.TYPE_OBJECT:
                instance = ModelCar.objects.get(id=value)
                validated_data[attribute_name] = instance
            else:
                validated_data[attribute_name] = value

        return validated_data

    @swagger_auto_schema(auto_schema=None)
    def get_swagger_fields(self):
        attributes = Attribute.objects.prefetch_related('enum_group__values').all()
        fields = {}

        for attribute in attributes:
            if attribute.datatype == Attribute.TYPE_OBJECT:
                # Для объекта Django используем PrimaryKeyRelatedField
                model = ModelCar
                fields[attribute.name] = serializers.PrimaryKeyRelatedField(queryset=model.objects.all())
            elif attribute.datatype == Attribute.TYPE_ENUM:
                # Для enum используем CharField с выбором
                choices = [(choice.value, choice.value) for choice in attribute.enum_group.values.all()]
                fields[attribute.name] = serializers.ChoiceField(choices=choices)
            else:
                # Для остальных типов данных используем CharField
                fields[attribute.name] = serializers.CharField(required=False, allow_null=True)

        return fields

    def get_fields(self):
        fields = super().get_fields()

        # Проверяем, используется ли сериализатор для документации
        if not hasattr(self, 'swagger_fake_view'):
            swagger_fields = self.get_swagger_fields()
            fields.update(swagger_fields)

        return fields
