from django.core.management import BaseCommand

from apps.car.tasks import create_car_models


class Command(BaseCommand):
    help = "seed database for testing and development."

    def handle(self, *args, **options):
        self.stdout.write('seeding data...')
        create_car_models.delay()
        self.stdout.write('done.')
