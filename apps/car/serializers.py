from rest_framework import serializers

from apps.car.models.Model import ModelCar, ManufacturerType
from apps.car.models.Modification import Modification, Engine


class ManufacturerTypeSerializer(serializers.ModelSerializer):
    class Meta:
        model = ManufacturerType
        fields = '__all__'


class ModelCarSerializer(serializers.ModelSerializer):
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
