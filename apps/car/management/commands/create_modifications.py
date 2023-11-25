import enum

from django.core.management import BaseCommand

from apps.car.models.Model import ModelCar
from apps.car.models.Modification import Modification
from apps.car.models.ModificationDetails import *
from base.requests import RecarRequest


class Command(BaseCommand):
    help = "seed database for testing and development."

    def handle(self, *args, **options):
        self.stdout.write('seeding data...')
        create_modifications()
        self.stdout.write('done.')


def create_modifications():
    recar_request = RecarRequest()
    body_types = dict(BodyTypeEnum.VALUES.value)
    drive_types = dict(DriveTypeEnum.VALUES.value)
    fuel_types = dict(FuelTypeEnum.VALUES.value)
    gear_types = dict(GearTypeEnum.VALUES.value)

    car_models = ModelCar.objects.values_list('id', flat=True)
    for car_model_id in car_models:
        modifications = []
        modifications_data = recar_request.get_modifications(modelId=car_model_id)
        for modification in modifications_data:
            modifications.append(
                Modification(id=modification['id'],
                             modelCar_id=int(modification['modelId']),
                             bodyType_id=body_types.get(modification['bodyType']),
                             driveType_id=drive_types.get(modification['driveType']),
                             fuelType_id=fuel_types.get(modification['fuelType']),
                             gearType_id=gear_types.get(modification['gearType']),
                             power=modification['power'],
                             numberOfCycle=modification['numOfCyl'],
                             numberOfValves=modification['numOfValves'],
                             capacity=modification['capacity'],
                             ))
        Modification.objects.bulk_create(modifications,
                                         unique_fields=['id'],
                                         ignore_conflicts=True)


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
