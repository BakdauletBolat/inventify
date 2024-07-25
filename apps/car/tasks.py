from celery import shared_task

from apps.car.actions.ImportModifcation import ImportModification


@shared_task
def import_modification(car_model_id: int):
    ImportModification().run(car_model_id)