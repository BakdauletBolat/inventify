import random

from django.core.management.base import BaseCommand
from loguru import logger

from apps.car.models.Model import *
from apps.car.models.Modification import Modification
from apps.car.models.ModificationDetails import *
from apps.category.models import Category
from apps.product.enums import StatusChoices
from apps.product.models.Price import Price
from apps.product.models.Product import Product
from base.requests import RecarRequest
from users.models.User import User

models = [Product, PlatformType, Price]
# python manage.py seed --mode=refresh

MODE_REFRESH = 'refresh'

""" Clear all data and do not create any object """
MODE_CLEAR = 'clear'


class Command(BaseCommand):
    help = "seed database for testing and development."

    def add_arguments(self, parser):
        parser.add_argument('--mode', type=str, help="Mode")

    def handle(self, *args, **options):
        self.stdout.write('seeding data...')
        run_seed(self, options['mode'])
        self.stdout.write('done.')


def clear_data():
    """Deletes all the table data"""
    logger.info("Delete seed instances")
    for model in models:
        model.objects.all().delete()


def create_product(index):
    modifications = Modification.objects.all()

    status_rand = random.choice(StatusChoices.choices)

    product = Product.objects.create(name=f"Product-{index}",
                                     code=index,
                                     market_price=index * 10,
                                     status=status_rand[0],
                                     modification=random.choice(modifications)
                                     )
    Price.objects.create(cost=999 * index, product=product)


def create_modification():
    logger.info("Creating ssed")

    bulk_create_options = {
        "update_conflicts": True,
        "unique_fields": ['id'],
        "update_fields": ['name']
    }

    categories = []
    bodies = []
    drive_types = []
    manufacturers = []
    colors = []
    steering_types = []
    fuel_types = []
    gear_types = []
    axles = [AxleConfiguration(name="Передняя"),
             AxleConfiguration(name="Задняя")]
    mileages = [MileageType(name="km"),
                MileageType(name="ml")]

    recar_request = RecarRequest()
    modification_params = recar_request.get_modification_params()

    for manufacturer in modification_params['manufacturers']['nodes']:
        manufacturers.append(ManufacturerType(id=manufacturer['id'],
                                              name=manufacturer['title']))

    for color in modification_params['colors']:
        colors.append(ColorType(id=color['id'],
                                name=color['name']))

    for fuelType in modification_params['fuelTypes']:
        fuel_types.append(FuelType(id=fuelType['id'],
                                   name=fuelType['name']))

    for bodyType in modification_params['bodyTypes']:
        bodies.append(BodyType(id=bodyType['id'],
                               name=bodyType['name']))

    for driveType in modification_params['driveTypes']:
        drive_types.append(DriveType(id=driveType['id'],
                                     name=driveType['name']))

    for gearType in modification_params['gearTypes']:
        gear_types.append(GearType(id=gearType['id'],
                                   name=gearType['name']))

    for steeringType in modification_params['steeringTypes']:
        steering_types.append(SteeringType(id=steeringType['id'],
                                           name=steeringType['name']))


    AxleConfiguration.objects.bulk_create(axles)
    BodyType.objects.bulk_create(bodies, **bulk_create_options)
    DriveType.objects.bulk_create(drive_types, **bulk_create_options)
    ManufacturerType.objects.bulk_create(manufacturers, **bulk_create_options)
    ColorType.objects.bulk_create(colors, **bulk_create_options)
    FuelType.objects.bulk_create(fuel_types, **bulk_create_options)
    GearType.objects.bulk_create(gear_types, **bulk_create_options)
    SteeringType.objects.bulk_create(steering_types, **bulk_create_options)
    MileageType.objects.bulk_create(mileages, **bulk_create_options)


def run_seed(self, mode):
    """ Seed database based on mode

    :param mode: refresh / clear
    :return:
    """
    # Clear data from tables
    clear_data()
    if mode == MODE_CLEAR:
        return
    try:
        User.objects.create_superuser(phone="+77089531792", password=123)
    except Exception:
        pass
    # Creating 15 addresses
    create_modification()
    for i in range(15):
        create_product(i)
