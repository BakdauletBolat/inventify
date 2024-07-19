from django.core.management import BaseCommand

from apps.product.enums import StatusChoices
from apps.product.models import Product
from apps.product.tasks import import_product_task
from base.requests import RecarRequest


class Command(BaseCommand):
    help = "seed database for testing and development."

    def handle(self, *args, **options):
        self.stdout.write('seeding data...')
        create_products()
        self.stdout.write('done.')


def create_products():
    products_recar = RecarRequest().get_products()
    product_ids = list(map(lambda x: int(x['id']), products_recar))
    products = Product.objects.filter(id__in=product_ids)
    difference_products = set(product_ids).difference(products.values_list('id', flat=True))
    for product_data in difference_products:
        import_product_task.delay(product_data)
