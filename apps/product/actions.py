import requests
from django.core.files.base import ContentFile
from django.db import transaction, utils

from apps.car.actions.ImportModifcation import ImportModification
from apps.car.models.Modification import Modification
from apps.product.enums import StatusChoicesRecar
from apps.product.models import Product
from apps.product.models.Price import Price
from apps.product.models.Product import ProductDetail, ProductImage
from apps.product.repository import ProductRepository
from base.requests import RecarRequest


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
    @transaction.atomic()
    def run(self, product_id: int):
        try:
            request = RecarRequest()
            product_data = request.get_product(product_id)
            modificaiton = request.get_product_modification(product_id)
            product = Product.objects.create(
                id=product_data['id'],
                name=product_data['category']['name'],
                market_price=product_data['suggestedPrice'],
                category_id=product_data['category']['id'],
                # color=
                defect=product_data['defectComment'],
                comment=product_data['comment'],
                # status=StatusChoicesRecar
                # mileage=
                # mileageType=
                modification_id=self.get_modification_id(modificaiton),
                warehouse_id=product_data['location']['id']
            )

            ProductDetail.objects.create(
                height=product_data['height'],
                width=product_data['width'],
                length=product_data['length'],
                weight=product_data['weight'],
                product=product
            )

            Price.objects.create(
                product=product,
                cost=0 if product_data.get('price') is None else product_data.get('price'),
            )

            for product_image in product_data['inputParent']['picturesV2']:
                image_url = product_image['optimized']
                response = requests.get(image_url)
                product_image = ProductImage(product=product)
                product_image.image.save(image_url.split("/")[-1], ContentFile(response.content))

        except utils.IntegrityError as exc:
            print(exc)

    @staticmethod
    def get_modification_id(modification_data: dict) -> Modification:

        try:
            modification = Modification.objects.get(id=modification_data['id'])
        except Modification.DoesNotExist:
            ImportModification().run(modification_data['modelId'])

        return modification_data['id']
