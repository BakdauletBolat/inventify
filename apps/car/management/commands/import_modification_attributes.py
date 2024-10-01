from django.core.management import BaseCommand

from apps.car.tasks import create_modifications_draft


class Command(BaseCommand):
    help = "seed database for testing and development."

    def handle(self, *args, **options):
        self.stdout.write('seeding data...')
        create_modifications()
        self.stdout.write('done.')


def create_modifications():
    create_modifications_draft()
