from celery import shared_task

from apps.product.models import Product
from apps.product.models.ImportProductData import ImportProductData
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
    batch_size = 10

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
