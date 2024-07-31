from celery import shared_task

from apps.product.actions import ImportProductAction
from apps.product.models.ImportProductData import ImportProductData
from base.requests import RecarRequest


@shared_task
def import_product_task(id: int):
    action = ImportProductAction()
    draft = ImportProductData.objects.get(id=id)
    action.run(draft.data)


@shared_task
def import_product_draft(product_id: int):
    request = RecarRequest()
    product_data = request.get_product(product_id)
    ImportProductData.objects.create(product_id=product_id, data=product_data)
