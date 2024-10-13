from rest_framework import serializers

from apps.car.models.Model import ModelCar, ManufacturerType
from apps.car.models.Modification import Modification, Engine
from apps.car.models.ModificationDetails import OemCodes, ColorType
from apps.stock.models import Quality


class ManufacturerTypeSerializer(serializers.ModelSerializer):
    class Meta:
        model = ManufacturerType
        fields = '__all__'


class ModelCarSerializer(serializers.ModelSerializer):
    manufacturer = ManufacturerTypeSerializer()

    class Meta:
        model = ModelCar
        fields = '__all__'


class EngineSerializer(serializers.ModelSerializer):
    class Meta:
        model = Engine
        fields = '__all__'


class ModificationSerializer(serializers.ModelSerializer):
    axleConfiguration = serializers.CharField()
    engines = serializers.SerializerMethodField()
    driveType = serializers.CharField()
    gearType = serializers.CharField()
    fuelType = serializers.CharField()
    bodyType = serializers.CharField()
    modelCar = ModelCarSerializer()

    @staticmethod
    def get_engines(obj):
        return EngineSerializer(obj.engine.all(), many=True).data

    class Meta:
        model = Modification
        fields = '__all__'


class OemCodesCreateIfNotExistField(serializers.ListSerializer):
    child = serializers.CharField()

    def to_internal_value(self, data):
        oem_codes = []
        for code in data:
            try:
                # Пытаемся найти объект OemCodes по коду
                oem_code = OemCodes.objects.get(code=code)
                oem_codes.append(oem_code)
            except OemCodes.DoesNotExist:
                # Если объект не найден, создаем новый
                oem_code = OemCodes.objects.create(code=code)
                oem_codes.append(oem_code)
        return oem_codes


class ColorTypeSerializer(serializers.ModelSerializer):
    class Meta:
        model = ColorType
        fields = '__all__'


class QualityTypeSerializer(serializers.ModelSerializer):
    class Meta:
        model = Quality
        fields = '__all__'
