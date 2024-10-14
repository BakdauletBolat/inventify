from django.core.management import BaseCommand

from apps.car.tasks import import_modification_recar


class Command(BaseCommand):
    help = "seed database for testing and development."

    def handle(self, *args, **options):
        self.stdout.write('seeding data...')
        import_modification_recar.delay()
        self.stdout.write('done.')
