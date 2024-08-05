import concurrent.futures

from django.core.management import BaseCommand

from apps.product.models import Product
from base.requests import RecarRequest


class Command(BaseCommand):
    help = "seed database for testing and development."

    def handle(self, *args, **options):
        self.stdout.write('seeding data...')
        update_modifications()
        self.stdout.write('done.')


def update_modifications():
    recar_request = RecarRequest()
    products_count = Product.objects.count()
    products_ids = Product.objects.values_list('id', flat=True)

    # Функция для получения модификации в потоке
    def get_modification(product_id):
        return recar_request.get_product_modification(product_id=product_id)

    for start in range(0, products_count, 1000):
        end = start + 500
        product_ids_batch = list(products_ids)[start:end]

        products = []
        with concurrent.futures.ThreadPoolExecutor(max_workers=4) as executor:
            future_to_product_id = {executor.submit(get_modification, product_id): product_id for product_id in product_ids_batch}
            for future in concurrent.futures.as_completed(future_to_product_id):
                product_id = future_to_product_id[future]
                try:
                    modification = future.result()
                    if modification is not None:
                        product = Product(
                            id=product_id,
                            modification_id=modification['id']
                        )
                        products.append(product)
                except Exception as exc:
                    print(f'Product {product_id} generated an exception: {exc}')

        # Обновляем все продукты одной партией
        Product.objects.bulk_update(products, ['modification_id'])