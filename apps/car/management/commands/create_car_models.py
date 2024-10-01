from django.core.management import BaseCommand

from apps.car.models.Model import ManufacturerType, ModelCar
from base.requests import RecarRequest
from apps.car.tasks import import_model_car


class Command(BaseCommand):
    help = "seed database for testing and development."

    def handle(self, *args, **options):
        self.stdout.write('seeding data...')
        create_models()
        self.stdout.write('done.')


def create_models():
    bulk_create_options = {
        "update_conflicts": True,
        "unique_fields": ['id'],
        "update_fields": ['name']
    }
    recar_request = RecarRequest()
    modification_params = recar_request.get_modification_params()
    manufacturers = []

    for manufacturer in modification_params['manufacturers']['nodes']:
        manufacturers.append(ManufacturerType(id=manufacturer['id'],
                                              name=manufacturer['title']))

    ManufacturerType.objects.bulk_create(manufacturers, **bulk_create_options)

    manufacturers = ManufacturerType.objects.values_list('id', flat=True)
    for manufacturer_id in manufacturers:
        import_model_car.apply(manufacturer_id)
