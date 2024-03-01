from django.core.management import BaseCommand

from apps.stock.actions import ImportWarehouseAction
from base.requests import RecarRequest


class Command(BaseCommand):
    help = "seed database for testing and development."

    def handle(self, *args, **options):
        self.stdout.write('import warehouse...')
        create_products()
        self.stdout.write('done.')


def create_products():
    warehouses = RecarRequest().get_warehouses()
    for warehouse in warehouses:
        ImportWarehouseAction().run(warehouse)
