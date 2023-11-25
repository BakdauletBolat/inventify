from django.core.management import BaseCommand

from apps.car.models.Model import ManufacturerType, ModelCar
from base.requests import RecarRequest


class Command(BaseCommand):
    help = "seed database for testing and development."

    def handle(self, *args, **options):
        self.stdout.write('seeding data...')
        create_models()
        self.stdout.write('done.')


def create_models():
    recar_request = RecarRequest()
    manufacturers = ManufacturerType.objects.values_list('id', flat=True)
    for manufacturer_id in manufacturers:
        cars = []
        car_models = recar_request.get_car_models(manufacturerId=manufacturer_id)
        for model in car_models:
            cars.append(ModelCar(startDate=model.get('startDate', None),
                                 endDate=model.get('endDate', None),
                                 id=model['id'],
                                 name=model['name'],
                                 manufacturer_id=manufacturer_id
                                 ))
        ModelCar.objects.bulk_create(cars,
                                     unique_fields=['id'],
                                     update_fields=['startDate'],
                                     update_conflicts=True)
