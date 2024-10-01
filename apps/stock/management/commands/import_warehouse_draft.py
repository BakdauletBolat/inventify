from django.core.management import BaseCommand

from apps.stock.tasks import import_warehouse_detail


class Command(BaseCommand):
    help = "seed database for testing and development."

    def handle(self, *args, **options):
        self.stdout.write('import warehouse...')
        import_warehouse_detail()
        self.stdout.write('done.')
