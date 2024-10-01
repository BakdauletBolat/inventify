from io import BytesIO

import requests
from PIL import Image
from django.core.files.base import ContentFile
from django.db import transaction, utils
from rest_framework.exceptions import ValidationError

from apps.car.models import ModificationDraft
from apps.car.tasks import update_eav_attr
from apps.product.enums import StatusChoicesRecar, StatusChoices
from apps.product.models.Price import Price
from apps.product.models.Product import ProductDetail, ProductImage, Product
from apps.product.repository import ProductRepository
from apps.stock.actions import StockAction
from apps.stock.models import Stock, Warehouse


class ProductAction:

    def create(self, data):
        with transaction.atomic():
            product = ProductRepository.create(**data)
            return product

    def update(self, product: Product, data):
        with transaction.atomic():
            instance = ProductRepository.update(product, **data)
            return instance

    def assign_to_warehouse(self, product: Product, warehouse: Warehouse):
        # Проверяем, что фотографии уже загружены
        if not product.pictures.exists():
            raise ValidationError("Сначала необходимо загрузить фотографии")

        # Привязываем продукт к складу
        stock = StockAction().process_ingoing(product, warehouse, 1)

        # Меняем статус на "в наличии"
        product.status = StatusChoices.IN_STOCK.value
        self.save_product(product)

        return stock

    @staticmethod
    def save_product(product: Product):
        """
        Сохраняет продукт и проверяет возможность изменения статуса.

        :param product: Продукт для сохранения.
        :raises ValidationError: Если статус изменен неправильно.
        """

        if product:  # Если продукт уже существует
            original = Product.objects.get(pk=product.pk)
            if original.status == StatusChoices.IN_STOCK.value and product.status != StatusChoices.IN_STOCK.value:
                raise ValidationError("Нельзя изменить статус обратно после установки 'в наличии'")

        product.save()


class ImportProductAction:

    @staticmethod
    def save_image(product_data, product):
        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/58.0.3029.110 Safari/537.36'
        }
        for product_image in product_data['inputParent']['picturesV2']:
            image_url = product_image['optimized']
            response = requests.get(image_url, headers=headers)
            image = Image.open(BytesIO(response.content))

            if image.mode == 'RGBA':
                image = image.convert('RGB')

            output_io = BytesIO()
            quality = 70  # Начальная качество
            max_size = 100 * 1024  # 100 КБ

            while True:
                output_io.truncate(0)
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
            modification_attr = ModificationDraft.objects.get(product_id=product.id)
            update_eav_attr(modification_attr)

            self.save_image(product_data, product)

        except utils.IntegrityError as exc:
            print(exc)
