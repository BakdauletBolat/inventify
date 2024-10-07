from django.db import transaction
from django.db.models import Sum
from rest_framework.exceptions import ValidationError

from apps.product.models.Product import Product
from apps.stock.enums import MovementEnum
from apps.stock.models import Warehouse, Stock, StockMovement
from apps.stock.repository import StockRepository, StockMovementRepository
from apps.stock.utils import update_quantity
from base.requests import RecarRequest


class StockAction:

    def __init__(self):
        self.stock_repository = StockRepository()
        self.movement_repository = StockMovementRepository()

    def move_product(self,
                     product: Product,
                     source_warehouse: Warehouse,
                     dest_warehouse: Warehouse,
                     quantity: int,
                     quality=None):
        """
        Перемещает товар с одного склада на другой.

        :param source_warehouse: Склад, с которого нужно переместить товар.
        :param target_warehouse: Склад, на который нужно переместить товар.
        :raises ValidationError: Если на складе недостаточно товара.
        :return: Список с двумя записями движения товара (отгрузка и поступление).
        """
        with transaction.atomic():
            # Выполняем отгрузку со склада-источника
            outgoing_movement = self.process_outgoing(product, source_warehouse, quantity, quality)

            # Выполняем поступление на целевой склад
            ingoing_movement = self.process_ingoing(product, dest_warehouse, quantity, quality)

            return [outgoing_movement, ingoing_movement]

    def process_outgoing(self, product: Product, warehouse: Warehouse, quantity: int, quality=None):
        """
            Уход товар с одного склада на другой.
        """
        return self.__process_movement(product, warehouse, MovementEnum.OUT, quantity, quality)

    def process_ingoing(self, product: Product, warehouse: Warehouse, quantity: int, quality=None):
        """
            Приход товар с одного склада на другой.
        """
        return self.__process_movement(product, warehouse, MovementEnum.IN, quantity, quality)

    def __process_movement(self,
                           product: Product,
                           warehouse: Warehouse,
                           movement_type: MovementEnum,
                           quantity: int,
                           quality=None):
        """
            Обрабатывает перемещение товара со склада.

            :param product: Продукт, который нужно отгрузить.
            :param warehouse: Склад, с которого нужно отгрузить товар.
            :param quantity: Количество товара для отгрузки.
            :param quality: Качество товара (если применимо).
            :raises ValidationError: Если на складе недостаточно товара.
            :return: Созданное движение товара.
        """

        # Получаем или создаем запись Stock
        stock = self.stock_repository.get_or_create_stock(product, warehouse, quality)

        # Проверка достаточности товара при отгрузке
        if movement_type == MovementEnum.OUT and quantity > stock.quantity:
            raise ValidationError("Недостаточно товара на складе для выполнения операции")

        # Применяем изменение количества
        update_quantity(stock, movement_type, quantity)

        # Создаем запись о движении
        movement = self.movement_repository.create(
            product=product,
            warehouse=warehouse,
            movement_type=movement_type,
            quality=stock.quality,
            quantity=quantity
        )

        return movement

    @staticmethod
    def get_aggregated_stock(category_id: int, warehouse_id: int):
        """
            Получает суммарное количество товара для заданной категории продуктов на указанном складе.
            :return: Словарь с ключом 'total_quantity' и значением, представляющим общее количество товара на складе для
             заданной категории. Если на складе нет товаров этой категории, возвращается 0.
            :rtype: int
        """

        return Stock.objects.filter(
            product__category_id=category_id,
            warehouse_id=warehouse_id
        ).aggregate(total_quantity=Sum('quantity', default=0))['total_quantity']

    @staticmethod
    def get_movement_quantity(category_id: int, movement_type: MovementEnum):
        """
            Получает общее количество для указанной категории продуктов и типа движения.

            :param category_id:
            :param movement_type: Тип движения (например, MovementEnum.IN или MovementEnum.OUT).
            :return: Суммарное количество для указанного типа движения.
        """
        return StockMovement.objects.filter(
            product__category_id=category_id,
            movement_type=movement_type
        ).aggregate(total=Sum('quantity', default=0))['total']


class ImportWarehouseAction:

    @staticmethod
    def run(warehouse_data):
        warehouse, created = Warehouse.objects.update_or_create(
            id=warehouse_data['id'],
            defaults={
                'name': warehouse_data['name'],
                'min_stock_level': warehouse_data.get('partsSpace', 10)
            }
        )

        category_ids = [category['id'] for category in warehouse_data['partCategories']]
        warehouse.products_category.set(category_ids)

    def import_detail(self, locationId):
        products = RecarRequest().get_warehouse_detail(locationId)
        stocks = []
        for product in products:
            stocks.append(Stock(
                warehouse_id=locationId,
                product_id=product['id'],
                quantity=1,
                quality_id=1
            ))

        Stock.objects.bulk_create(stocks,
                                  ignore_conflicts=True)
