from django.core.management import BaseCommand

from apps.product.enums import StatusChoices
from apps.product.models.Product import Product
from base.requests import RecarRequest


class Command(BaseCommand):
    help = "seed database for testing and development."

    def handle(self, *args, **options):
        self.stdout.write('seeding data...')
        update_status()
        self.stdout.write('done.')


def update_status():
    products_not_parsed = RecarRequest().get_products(['not_parsed'])
    products_in_stock = RecarRequest().get_products(['in_stock'])
    products_sold = RecarRequest().get_products(['sold'])
    products_deleted = RecarRequest().get_products(['deleted'])
    Product.objects.filter(id__in=get_products_id(products_not_parsed)).update(status=StatusChoices.RAW)
    Product.objects.filter(id__in=get_products_id(products_in_stock)).update(status=StatusChoices.IN_STOCK)
    Product.objects.filter(id__in=get_products_id(products_sold)).update(status=StatusChoices.SOLD)
    Product.objects.filter(id__in=get_products_id(products_deleted)).update(status=StatusChoices.DELETED)


def get_products_id(products: list):
    return list(map(lambda x: int(x['id']), products))
