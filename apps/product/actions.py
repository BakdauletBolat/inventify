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
    # {
    #     "id": "23344374",
    #     "visible": true,
    #     "comment": null,
    #     "defective": false,
    #     "status": "in_stock",
    #     "defectComment": null,
    #     "price": null,
    #     "nearestParentId": null,
    #     "children": [
    #         {
    #             "price": null,
    #             "status": "in_stock",
    #             "id": "23344374",
    #             "nearestParentId": null,
    #             "__typename": "Part"
    #         }
    #     ],
    #     "department": {
    #         "id": "9182",
    #         "name": "Kaynar Avto",
    #         "__typename": "Department"
    #     },
    #     "category": {
    #         "id": "2660",
    #         "name": "Молдинг задней правой двери",
    #         "__typename": "PartCategory"
    #     },
    #     "oemCodes": [
    #         {
    #             "id": "15791084",
    #             "code": "2106901062",
    #             "__typename": "OemCode"
    #         }
    #     ],
    #     "location": {
    #         "id": "1085726",
    #         "name": "Шар-Шара1L6/2",
    #         "departmentId": "9182",
    #         "__typename": "Location"
    #     },
    #     "picturesV2": [
    #         {
    #             "id": "9480ec33-1e7d-42e9-a2a8-eae2b9560e96",
    #             "order": "0",
    #             "status": "resized",
    #             "s195x130": "https://d1ef4a9755q128.cloudfront.net/images/3nzKnqYlOY/195x130/23344374_9480ec33-1e7d-42e9-a2a8-eae2b9560e96.jpeg",
    #             "s360x240": "https://d1ef4a9755q128.cloudfront.net/images/3nzKnqYlOY/360x240/23344374_9480ec33-1e7d-42e9-a2a8-eae2b9560e96.jpeg",
    #             "s570x380": "https://d1ef4a9755q128.cloudfront.net/images/3nzKnqYlOY/570x380/23344374_9480ec33-1e7d-42e9-a2a8-eae2b9560e96.jpeg",
    #             "__typename": "PictureV2"
    #         }
    #     ],
    #     "vehicleSpecifications": {
    #         "id": "11840844",
    #         "vinCode": null,
    #         "manufacturer": {
    #             "id": "1621",
    #             "name": "MERCEDES-BENZ",
    #             "__typename": "Manufacturer"
    #         },
    #         "model": {
    #             "id": "795",
    #             "name": "E (W210)",
    #             "startDate": "1995-05-31",
    #             "endDate": "2003-07-31",
    #             "__typename": "Model"
    #         },
    #         "modification": {
    #             "id": "8106",
    #             "name": "E 220 CDI (210.006)",
    #             "power": 105,
    #             "__typename": "Modification"
    #         },
    #         "year": 1998,
    #         "gearType": "АКПП",
    #         "fuelType": "Дизель",
    #         "bodyType": "Cедан",
    #         "engineDisplacement": 2.2,
    #         "color": null,
    #         "steeringType": "LHD",
    #         "__typename": "VehicleSpecifications"
    #     },
    #     "__typename": "Part"
    # }

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
