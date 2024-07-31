import time

from django.core.management import BaseCommand

from apps.product.enums import StatusChoices
from apps.product.models import Product, ImportProductData
from apps.product.tasks import import_product_task
from base.requests import RecarRequest


class Command(BaseCommand):
    help = "seed database for testing and development."

    def handle(self, *args, **options):
        self.stdout.write('seeding data...')
        create_products()
        self.stdout.write('done.')


def create_products():
    product_ids_recar = ImportProductData.objects.values_list('product_id', flat=True)
    products = Product.objects.filter(id__in=product_ids_recar).values_list('id', flat=True)
    difference_products_ids = set(product_ids_recar).difference(products)
    batch_size = 10
    interval = 5  # Интервал между отправками задач в секундах

    for start in range(0, len(difference_products_ids), batch_size):
        end = start + batch_size
        batch_ids = list(difference_products_ids)[start:end]
        remains_recar_products = ImportProductData.objects.filter(product_id__in=batch_ids)

        for product_data in remains_recar_products:
            import_product_task.delay(product_data.id)

        time.sleep(interval)  # Задержка между пакетами задач
