from django.core.management import BaseCommand

from apps.product.enums import StatusChoices
from apps.product.models.Product import Product
from apps.product.tasks import update_status_products
from base.requests import RecarRequest


class Command(BaseCommand):
    help = "seed database for testing and development."

    def handle(self, *args, **options):
        self.stdout.write('seeding data...')
        update_status_products()
        self.stdout.write('done.')



