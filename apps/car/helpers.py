import enum

from apps.car.models.ModificationDetails import *


class AxleConfigurationEnum(enum.Enum):
    # Создайте элементы enum на основе значений поля your_field
    @staticmethod
    def get_values():
        return [(item.name, item.id) for item in AxleConfiguration.objects.all()]


class BodyTypeEnum(enum.Enum):
    # Создайте элементы enum на основе значений поля your_field
    @staticmethod
    def get_values():
        return [(item.name, item.id) for item in BodyType.objects.all()]


class SteeringTypeEnum(enum.Enum):
    # Создайте элементы enum на основе значений поля your_field
    @staticmethod
    def get_values():
        return [(item.name, item.id) for item in SteeringType.objects.all()]


class DriveTypeEnum(enum.Enum):
    # Создайте элементы enum на основе значений поля your_field
    @staticmethod
    def get_values():
        return [(item.name, item.id) for item in DriveType.objects.all()]


class FuelTypeEnum(enum.Enum):
    # Создайте элементы enum на основе значений поля your_field
    @staticmethod
    def get_values():
        return [(item.name, item.id) for item in FuelType.objects.all()]


class GearTypeEnum(enum.Enum):
    # Создайте элементы enum на основе значений поля your_field
    @staticmethod
    def get_values():
        return [(item.name, item.id) for item in GearType.objects.all()]
