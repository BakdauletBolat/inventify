from celery import shared_task

from apps.product.enums import StatusChoices
from apps.product.models import Product
from apps.product.models.ImportProductData import ImportProductData
from apps.product.models.Price import Price
from apps.product.repository import ProductRepository
from base.requests import RecarRequest


@shared_task
def import_product_task(id: int):
    from apps.product.actions import ImportProductAction
    action = ImportProductAction()
    draft = ImportProductData.objects.get(id=id)
    action.run(draft.data)


@shared_task
def import_product_draft(product_id: int):
    request = RecarRequest()
    product_data = request.get_product(product_id)
    ImportProductData.objects.create(product_id=product_id, data=product_data)


@shared_task
def create_products():
    product_ids_recar = ImportProductData.objects.values_list('product_id', flat=True)
    products = Product.objects.filter(id__in=product_ids_recar).values_list('id', flat=True)
    difference_products_ids = set(product_ids_recar).difference(products)
    batch_size = 100

    for start in range(0, len(difference_products_ids), batch_size):
        end = start + batch_size
        batch_ids = list(difference_products_ids)[start:end]
        remains_recar_products = ImportProductData.objects.filter(product_id__in=batch_ids)

        for product_data in remains_recar_products:
            import_product_task.delay(product_data.id)


@shared_task
def create_products_draft():
    products_recar = RecarRequest().get_products()
    product_ids = list(map(lambda x: int(x['id']), products_recar))
    products = ImportProductData.objects.filter(product_id__in=product_ids)
    diffrence_products = set(product_ids).difference(products.values_list('product_id', flat=True))
    for product_data in diffrence_products:
        import_product_draft.delay(product_data)


# Размер порции для UPDATE ... WHERE id IN (...): при сотнях тысяч id
# один запрос раздувает и память процесса, и план запроса в postgres.
STATUS_UPDATE_BATCH_SIZE = 5000

# Статус в Recar -> статус товара у нас
RECAR_STATUS_MAP = (
    ('not_parsed', StatusChoices.RAW),
    ('in_stock', StatusChoices.IN_STOCK),
    ('sold', StatusChoices.SOLD),
    ('deleted', StatusChoices.DELETED),
)


@shared_task
def update_status_products():
    """Синхронизирует статусы товаров с Recar.

    Статусы обрабатываются строго по одному, а обновление идёт порциями:
    выборка Recar отдаёт до 200 000 записей на статус, и держать в памяти
    все четыре списка сразу сервер не переживает.
    """
    for recar_status, status in RECAR_STATUS_MAP:
        product_ids = get_products_id(RecarRequest().get_products([recar_status]))

        for start in range(0, len(product_ids), STATUS_UPDATE_BATCH_SIZE):
            batch_ids = product_ids[start:start + STATUS_UPDATE_BATCH_SIZE]
            Product.objects.filter(id__in=batch_ids).update(status=status)

        # Освобождаем память до следующего запроса в Recar
        del product_ids


# Задача отключена намеренно: обновление цен не используется, из beat_schedule убрано.
# Прежде чем включать обратно — переписать: сейчас тут перебор всех цен вложенным
# циклом (next(filter(...)) внутри цикла по товарам) и весь список Price в памяти,
# на сотнях тысяч товаров это часы работы и сотни мегабайт.
# @shared_task
def update_price():
    products_recar = RecarRequest().get_products()
    prices = []
    prices_with_id = Price.objects.values('id', 'product_id')
    for product in products_recar:

        try:
            price_id = next(filter(lambda x: x['product_id'] == int(product['id']), prices_with_id))
        except StopIteration:
            continue

        prices.append(Price(
            id=price_id['id'],
            cost=0 if product.get('price') is None else int(product.get('price')),
        ))

    Price.objects.bulk_update(prices, ['cost'])


def get_products_id(products: list):
    return list(map(lambda x: int(x['id']), products))


@shared_task
def import_parent_products():
    from apps.product.actions import ImportProductAction
    action = ImportProductAction()
    products = ImportProductData.objects.exclude(data__nearestParentId=None)
    for product in products:
        action.input_parent(product.data)


@shared_task
def import_pictures_from_recar(product_id: int):
    product = ProductRepository().get(product_id)
    from apps.product.actions import ImportProductAction
    action = ImportProductAction()
    action.save_image(product=product)
