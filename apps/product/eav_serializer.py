from eav.models import Attribute
from rest_framework import serializers

from apps.car.models.Model import ModelCar
from apps.car.serializers import ModelCarSerializer


class ProductEAVSerializer(serializers.Serializer):

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        # Добавляем поля в сериализатор динамически
        for attribute in Attribute.objects.all():
            if attribute.datatype == Attribute.TYPE_OBJECT:
                # Для объекта Django используем PrimaryKeyRelatedField
                model = ModelCar
                self.fields[attribute.slug] = serializers.PrimaryKeyRelatedField(queryset=model.objects.all())
            elif attribute.datatype == Attribute.TYPE_ENUM:
                # Для enum используем CharField с выбором
                choices = [(choice.value, choice.value) for choice in attribute.enum_group.values.all()]
                self.fields[attribute.slug] = serializers.ChoiceField(choices=choices)
            else:
                # Для остальных типов данных используем CharField
                self.fields[attribute.slug] = serializers.CharField(required=False, allow_null=True)

    def to_representation(self, instance):
        attributes = {}
        for attribute in Attribute.objects.all():
            # Используем getattr для доступа к значению EAV-атрибута
            value = getattr(instance.eav, attribute.slug, None)
            if attribute.datatype == Attribute.TYPE_OBJECT:
                if value is not None:
                    value = ModelCarSerializer(getattr(instance.eav, attribute.slug, None)).data
                    # value.pop('_state')
            if attribute.datatype == Attribute.TYPE_ENUM:
                value = value if value is not None else getattr(value, 'value', None)

            attributes[attribute.name] = value
        return attributes

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
