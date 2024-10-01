from django.core.management import BaseCommand

from apps.product.tasks import create_products_draft


class Command(BaseCommand):
    help = "seed database for testing and development."

    def handle(self, *args, **options):
        self.stdout.write('seeding data...')
        create_products_draft()
        self.stdout.write('done.')
