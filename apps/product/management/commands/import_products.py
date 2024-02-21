from django.core.management import BaseCommand

from apps.car.actions.ImportModifcation import ImportModification
from apps.car.models.Model import ModelCar
from apps.product.actions import ImportProductAction


class Command(BaseCommand):
    help = "seed database for testing and development."

    def handle(self, *args, **options):
        self.stdout.write('seeding data...')
        create_modifications()
        self.stdout.write('done.')


def create_modifications():
    car_models = ModelCar.objects.values_list('id', flat=True)
    for product_data in car_models:
        product = ImportProductAction().run(product_data)
