from io import BytesIO

import requests
from PIL import Image
from django.core.files.base import ContentFile
from django.db import transaction, utils

from apps.car.actions.ImportModifcation import ImportModification
from apps.car.models.Modification import Modification
from apps.product.enums import StatusChoicesRecar
from apps.product.models import Product
from apps.product.models.Price import Price
from apps.product.models.Product import ProductDetail, ProductImage
from apps.product.repository import ProductRepository
from apps.stock.models import Stock
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

    @staticmethod
    def save_image(product_data, product):
        for product_image in product_data['inputParent']['picturesV2']:
            image_url = product_image['optimized']
            response = requests.get(image_url)
            image = Image.open(BytesIO(response.content))

            output_io = BytesIO()
            quality = 70  # Начальная качество
            max_size = 1 * 1024 * 1024  # 1 МБ

            while True:
                output_io.seek(0)
                image.save(output_io, format='JPEG', quality=quality)
                output_io.seek(0)
                if len(output_io.getvalue()) <= max_size or quality < 10:
                    break
                quality -= 5  # Уменьшение качества на 5%

            product_image_instance = ProductImage(product=product)
            product_image_instance.image.save(image_url.split("/")[-1], ContentFile(output_io.getvalue()))

            # Очистка буфера
            output_io.close()

    @transaction.atomic()
    def run(self, product_data: dict):
        try:
            request = RecarRequest()
            modificaiton = request.get_product_modification(product_data['id'])
            product = Product.objects.create(
                id=product_data['id'],
                name=product_data['category']['name'],
                market_price=None if product_data.get('suggestedPrice') is None else product_data.get(
                    'suggestedPrice').get('currentPrice'),
                category_id=product_data['category']['id'],
                # color=
                defect=product_data['defectComment'],
                comment=product_data['comment'],
                status=StatusChoicesRecar.__getitem__(name=product_data['status']),
                # mileage=
                # mileageType=
                modification_id=modificaiton['id'],
            )

            Stock.objects.create(
                product=product,
                warehouse_id=None if product_data.get('location') is None else product_data.get('location')['id'],
                quality_id=1,
                quantity=1
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

            self.save_image(product_data, product)

        except utils.IntegrityError as exc:
            print(exc)

    @staticmethod
    def get_modification_id(modification_data: dict) -> Modification:

        try:
            modification = Modification.objects.get(id=modification_data['id'])
        except Modification.DoesNotExist:
            ImportModification().run(modification_data['modelId'])

        return modification_data['id']
