from django.db import transaction

from apps.car.actions.ImportModifcation import ImportModification
from apps.car.models.Modification import Modification
from apps.product.enums import StatusChoices
from apps.product.models import Product
from apps.product.repository import ProductRepository
from apps.stock.models import Warehouse


class CreateProductAction:

    def __init__(self, data):
        self.data = data

    def run(self):
        with transaction.atomic():
            product = ProductRepository.create(**self.data)
            return product


class UpdateProductAction:

    def __init__(self, data):
        self.data = data

    def run(self, instance):
        with transaction.atomic():
            product = ProductRepository.update(instance, **self.data)
            return product


class ImportProductAction:
    def run(self, product_data: dict) -> Product:

        warehouse = Warehouse.objects.get_or_create(id=product_data.get('id'),
                                                    defaults={
                                                        "name": product_data.get('name')
                                                    })
        category = product_data.get('category', '')

        product = Product(
            name=category.get('name', ''),
            warehouse=warehouse,
            modification=self.get_modification(product_data),
            category_id=category.get('id', None),
            defect=product_data.get('defectComment', ''),
            comment=product_data.get('comment', ''),
            status=StatusChoices.IN_STOCK.value if product_data.get('status') == 'in_stock' else StatusChoices.RAW.value
        )

        return product

    @staticmethod
    def get_modification(product_data: dict) -> Modification:
        modification_id = product_data['vehicleSpecifications']['modification']['id']
        modification = None

        try:
            modification = Modification.objects.get(id=modification_id)
        except modification.DoesNotExist:
            ImportModification().run(product_data['vehicleSpecifications']['model']['id'])
            modification = Modification.objects.get(id=modification_id)

        return modification
