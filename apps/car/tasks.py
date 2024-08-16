from celery import shared_task

from apps.car.actions.ImportModifcation import ImportModification
from apps.car.models.ModificationDraft import ModificationDraft
from base.requests import RecarRequest


@shared_task
def import_modification(car_model_id: int):
    ImportModification().run(car_model_id)


@shared_task
def import_modification_draft(product_id: int):
    request = RecarRequest()
    modification = request.get_product_modification(product_id)
    ModificationDraft.objects.create(
        product_id=product_id,
        data=modification
    )
