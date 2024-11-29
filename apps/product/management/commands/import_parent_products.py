from django.core.management import BaseCommand

from apps.product.tasks import import_parent_products


class Command(BaseCommand):
    help = "seed database for testing and development."

    def handle(self, *args, **options):
        self.stdout.write('seeding data...')
        import_parent_products()
        self.stdout.write('done.')
