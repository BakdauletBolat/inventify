from django.core.management import BaseCommand

from apps.car.models.ModificationDraft import ModificationDraft
from apps.car.tasks import import_modification_draft
from base.requests import RecarRequest


class Command(BaseCommand):
    help = "seed database for testing and development."

    def handle(self, *args, **options):
        self.stdout.write('seeding data...')
        create_modifications()
        self.stdout.write('done.')


def create_modifications():
    products_recar = RecarRequest().get_products()
    product_ids = list(map(lambda x: int(x['id']), products_recar))
    products = ModificationDraft.objects.filter(product_id__in=product_ids)
    difference_products = set(product_ids).difference(products.values_list('product_id', flat=True))
    for product_id in difference_products:
        import_modification_draft.delay(product_id)

