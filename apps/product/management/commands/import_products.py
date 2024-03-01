from django.core.management import BaseCommand

from apps.car.models.Model import ModelCar
from apps.product.actions import ImportProductAction
from base.requests import RecarRequest


class Command(BaseCommand):
    help = "seed database for testing and development."

    def handle(self, *args, **options):
        self.stdout.write('seeding data...')
        create_products()
        self.stdout.write('done.')


def create_products():
    products = RecarRequest().get_products()
    for product_data in products:
        ImportProductAction().run(product_data['id'])
