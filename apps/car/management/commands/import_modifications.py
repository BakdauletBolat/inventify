from django.core.management import BaseCommand

from apps.car.actions.ImportModifcation import ImportModification
from apps.car.models.Model import ModelCar


class Command(BaseCommand):
    help = "seed database for testing and development."

    def handle(self, *args, **options):
        self.stdout.write('seeding data...')
        create_modifications()
        self.stdout.write('done.')


def create_modifications():
    car_models = ModelCar.objects.values_list('id', flat=True)
    for car_model_id in car_models:
        ImportModification().run(car_model_id)
