from django.core.management import BaseCommand

from apps.car.models.Modification import Modification, Engine
from base.requests import RecarRequest


class Command(BaseCommand):
    help = "seed database for testing and development."

    def handle(self, *args, **options):
        self.stdout.write('seeding data...')
        create_engines()
        self.stdout.write('done.')


def create_engines():
    recar_request = RecarRequest()

    modifications = Modification.objects.values_list('id', flat=True)

    for modification_id in modifications:
        engines = []
        engines_data = recar_request.get_engines(modification_id)
        for engine in engines_data:
            engines.append(Engine(id=engine['id'],
                                  name=engine['name'],
                                  modification_id=modification_id))
        Engine.objects.bulk_create(engines,
                                   ignore_conflicts=True)
