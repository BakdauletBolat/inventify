from django.core.management import BaseCommand

from apps.car.tasks import create_engines


class Command(BaseCommand):
    help = "seed database for testing and development."

    def handle(self, *args, **options):
        self.stdout.write('seeding data...')
        create_engines()
        self.stdout.write('done.')
