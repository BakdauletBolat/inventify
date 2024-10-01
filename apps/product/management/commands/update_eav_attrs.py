from django.core.management import BaseCommand

from apps.car.models.ModificationDraft import ModificationDraft
from apps.car.tasks import update_eav_attr
from apps.product.models import Product


class Command(BaseCommand):
    help = "seed database for testing and development."

    def handle(self, *args, **options):
        self.stdout.write('seeding data...')
        update_eav_attrs()
        self.stdout.write('done.')


def update_eav_attrs():
    product_ids = Product.objects.values_list('id', flat=True)

    batch_size = 1000
    for start in range(0, len(product_ids), batch_size):
        end = start + batch_size
        batch_ids = list(product_ids)[start:end]
        modification_attrs = ModificationDraft.objects.filter(product_id__in=batch_ids)

        for modification_attr in modification_attrs:
            update_eav_attr.delay(modification_attr.data, modification_attr.product_id)
