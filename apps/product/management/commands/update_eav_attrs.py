from django.core.management import BaseCommand
from eav.models.enum_value import EnumValue

from apps.car.models import ModelCar
from apps.car.models.ModificationDraft import ModificationDraft
from apps.product.models import Product


class Command(BaseCommand):
    help = "seed database for testing and development."

    def handle(self, *args, **options):
        self.stdout.write('seeding data...')
        create_products()
        self.stdout.write('done.')


def create_products():
    product_ids = Product.objects.values_list('id', flat=True)

    batch_size = 1000
    for start in range(0, len(product_ids), batch_size):
        end = start + batch_size
        batch_ids = list(product_ids)[start:end]
        modification_attrs = ModificationDraft.objects.filter(product_id__in=batch_ids)

        for modification_attr in modification_attrs:
            modification = modification_attr.data.get('modification') if modification_attr.data.get('modification') is not None else {}
            product = Product.objects.get(
                id=modification_attr.product_id,
            )

            product.mileage = modification_attr.data['mileage']

            product.eav.bodytype = modification_attr.data['bodyType']
            product.eav.fueltype = modification_attr.data['fuelType']
            product.eav.geartype = modification_attr.data['gearType']
            product.eav.drivetype = modification_attr.data['driveType']
            product.eav.steeringtype = modification_attr.data['steeringType']
            product.eav.axleconfiguration = modification_attr.data['axleConfiguration']
            try:
                product.eav.modelCar = ModelCar.objects.get(id=modification_attr.data['model']['id'])
            except Exception as e:
                print(modification_attr.id)
            product.eav.power = modification.get('power', None)
            product.eav.capacity = modification.get('capacity', None)
            product.eav.numberofcycle = modification.get('numOfCyl', None)
            product.eav.numberofvalves = modification.get('numOfValves', None)
            product.eav.enginedisplacement = modification.get('engineDisplacement', None)
            product.save()