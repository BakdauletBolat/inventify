import enum

from apps.car.models.ModificationDetails import *


class BodyTypeEnum(enum.Enum):
    # Создайте элементы enum на основе значений поля your_field
    VALUES = [(item.name, item.id) for item in BodyType.objects.all()]


class DriveTypeEnum(enum.Enum):
    # Создайте элементы enum на основе значений поля your_field
    VALUES = [(item.name, item.id) for item in DriveType.objects.all()]


class FuelTypeEnum(enum.Enum):
    # Создайте элементы enum на основе значений поля your_field
    VALUES = [(item.name, item.id) for item in FuelType.objects.all()]


class GearTypeEnum(enum.Enum):
    # Создайте элементы enum на основе значений поля your_field
    VALUES = [(item.name, item.id) for item in GearType.objects.all()]