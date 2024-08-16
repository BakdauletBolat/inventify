from django.core.management import BaseCommand
from eav.models import Attribute
from eav.models.enum_group import EnumGroup
from eav.models.enum_value import EnumValue

from apps.car.models import *


class Command(BaseCommand):
    help = "seed database for testing and development."

    def handle(self, *args, **options):
        self.stdout.write('seeding data...')
        create_modifications()
        self.stdout.write('done.')


def create_eav_enum_attribute(name, description, enum_group=None, datatype=Attribute.TYPE_ENUM):
    return Attribute.objects.get_or_create(
        name=name,
        datatype=datatype,
        description=description,
        enum_group=enum_group
    )


def create_enum_group(name, model_instances):
    enum_group, created = EnumGroup.objects.get_or_create(name=name)
    enum_values = []

    for instance in model_instances:
        enum_value, created = EnumValue.objects.get_or_create(value=str(instance.name))
        enum_values.append(enum_value)
    enum_group.values.set(enum_values)
    return enum_group


def create_modifications():
    # Создание enum-групп и привязка значений
    axle_enum_group = create_enum_group('AxleConfiguration', AxleConfiguration.objects.all())
    body_enum_group = create_enum_group('BodyType', BodyType.objects.all())
    drive_enum_group = create_enum_group('DriveType', DriveType.objects.all())
    gear_enum_group = create_enum_group('GearType', GearType.objects.all())
    fuel_enum_group = create_enum_group('FuelType', FuelType.objects.all())
    streeting_type_enum_group = create_enum_group('SteeringType', SteeringType.objects.all())

    create_eav_enum_attribute('axleConfiguration', 'Тип оси', axle_enum_group)
    create_eav_enum_attribute('steeringType', 'Тип рулевого управления', streeting_type_enum_group)
    create_eav_enum_attribute('bodyType', 'Тип кузова', body_enum_group)
    create_eav_enum_attribute('driveType', 'Тип вождения (руль)', drive_enum_group)
    create_eav_enum_attribute('gearType', 'Тип кпп', gear_enum_group)
    create_eav_enum_attribute('fuelType', 'Тип топлива', fuel_enum_group)
    create_eav_enum_attribute('modelCar', 'Модель машины', datatype=Attribute.TYPE_OBJECT)
    create_eav_enum_attribute('engine', 'Двигатель', datatype=Attribute.TYPE_OBJECT)
    create_eav_enum_attribute('capacity', 'Вместимость (объем мотора)', datatype=Attribute.TYPE_FLOAT)
    create_eav_enum_attribute('power', 'Мощность', datatype=Attribute.TYPE_INT)
    create_eav_enum_attribute('numberOfCycle', 'Количество шин', datatype=Attribute.TYPE_INT)
    create_eav_enum_attribute('numberOfValves', 'Количество клапанов', datatype=Attribute.TYPE_INT)
    create_eav_enum_attribute('vinCode', 'Вин код', datatype=Attribute.TYPE_TEXT)
    create_eav_enum_attribute('engineDisplacement', 'Вместимость', datatype=Attribute.TYPE_FLOAT)

