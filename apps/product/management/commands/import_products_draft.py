from django.core.management import BaseCommand

from apps.product.enums import StatusChoices
from apps.product.models import Product
from apps.product.models.ImportProductData import ImportProductData
from apps.product.tasks import import_product_task, import_product_draft
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
    products = ImportProductData.objects.filter(product_id__in=product_ids)
    diffrence_products = set(product_ids).difference(products.values_list('product_id', flat=True))
    for product_data in diffrence_products:
        import_product_draft.delay(product_data)
