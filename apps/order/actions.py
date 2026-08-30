import logging
from typing import List

from django.core.exceptions import ValidationError
from django.db.utils import DataError
from django.utils.translation import gettext as _

from apps.order.enums import *
from apps.order.models import Order, OrderItem
from apps.product.enums import StatusChoices
from apps.product.models.Product import Product
from apps.stock.actions import StockAction
from apps.stock.models import Warehouse


logger = logging.getLogger(__name__)


def _map_recar_value(mapping, raw_value, default, field_name, order_id):
    """Переводит значение Recar в наше перечисление.

    Recar заводит новые статусы и типы оплаты, не предупреждая. Неизвестное
    значение не должно ронять импорт всего заказа: подставляем значение по
    умолчанию и пишем предупреждение, чтобы расхождение было видно в логах.
    """
    try:
        return mapping[raw_value]
    except KeyError:
        logger.warning(
            'Recar прислал неизвестный %s=%r у заказа %s — подставлено %s',
            field_name, raw_value, order_id, default.label,
        )
        return default


class ImportOrderAction:
    def run(self, order_data: dict):
        order_id = order_data['id']

        order = Order(
            id=order_id,
            payment_type=_map_recar_value(
                RECAR_PAYMENT_TYPE_MAP, order_data['paymentType'],
                PaymentTypeChoices.CASH, 'paymentType', order_id,
            ),
            payment_status=PaymentStatusChoices.PAID if order_data['paymentCompleted'] else PaymentStatusChoices.FAILED,
            status=
            _map_recar_value(
                RECAR_ORDER_STATUS_MAP, order_data['status'],
                OrderStatusChoices.PROCESSING, 'status', order_id,
            )
            if order_data['returning'] is False
            else OrderStatusChoices.REFUNDED,
            total=order_data['totalPrice'],
            comment=order_data['comment'],
            warehouse_id=order_data['location']['id'],
            refund_order_id=None if order_data.get('parentOrder', None) is None else order_data['parentOrder']['id'],
            created_at=order_data['createdAt'],
            updated_at=order_data['updatedAt']
        )
        try:
            order.save()
        except DataError as e:
            order.total = int(order_data['totalPrice'] / 100)
            order.save()

        for item in order_data['partsSnapshot']:
            if item['nearestParentId'] is None:
                OrderItem.objects.create(
                    product_id=item['id'],
                    order=order,
                    is_returning=True if item['returning'] is True else False
                )


class OrderAction:

    def __init__(self, data=None):
        if data is None:
            data = {}
        self.data = data
        self.goods = self.data.pop('goods', [])

    def create(self):
        self.set_total()
        order = Order.objects.create(**self.data)
        self.__create_order_items(order)
        products = [item['product'] for item in self.goods]
        self._update_status_products(StatusChoices.RESERVED, products)
        return order

    def outgoing_order(self, products: List[Product]):
        stock = StockAction()
        for product in products:
            stock.process_outgoing(product, product.warehouse, 1)

    def ingoing_order(self, products: List[Product], warehouse: Warehouse):
        stock = StockAction()
        for product in products:
            stock.process_ingoing(product, warehouse, 1)

    def delete(self, order: Order):
        self.__update_order_status_failure(order)
        products = list(Product.objects.filter(order_item__order=order))
        self._update_status_products(StatusChoices.IN_STOCK, products)
        order.save()

    def refund(self):
        self.set_total()
        order = Order.objects.create(**self.data)
        self.__create_order_items(order)
        products = Product.objects.filter(order_item__order=order)
        self.__set_is_returning_products(order.refund_order)
        self._update_status_products(StatusChoices.IN_STOCK, list(products))
        self.__update_order_status_refunded(order)
        self.ingoing_order(products, order.warehouse)
        return order

    def confirm(self, order: Order):
        self.__update_order_status_success(order)
        products = list(Product.objects.filter(order_item__order=order))
        self.outgoing_order(products)
        self._update_status_products(StatusChoices.SOLD, products)
        return order

    def set_total(self) -> None:
        self.data['total'] = sum(list(
            map(
                lambda x: getattr(x['product'].price.last(), 'cost', 0) * x['quantity'], self.goods
            )
        ))

    def _update_status_products(self, status: StatusChoices, items: List[Product]):
        products = []
        for item in items:
            item.status = status
            products.append(item)

        Product.objects.bulk_update(products, ['status'])

    def __create_order_items(self, order: Order):
        for item in self.goods:
            item['order_id'] = order.id
            OrderItem.objects.create(**item)

    @staticmethod
    def __update_order_status_success(order: Order):
        if order.payment_status == PaymentStatusChoices.PAID \
                and order.payment_type == PaymentTypeChoices.INTERNET_PAYMENT:
            order.status = OrderStatusChoices.COMPLETED
            order.save()

        elif order.payment_type == PaymentTypeChoices.CASH:
            order.status = OrderStatusChoices.COMPLETED
            order.payment_status = PaymentStatusChoices.PAID
            order.save()
        else:
            raise ValidationError(_('Заказ не оплачен, либо отклонен'))

    @staticmethod
    def __update_order_status_failure(order: Order):
        order.status = OrderStatusChoices.CANCELED
        order.payment_status = PaymentStatusChoices.FAILED
        order.save()

    @staticmethod
    def __update_order_status_refunded(order: Order):
        order.status = OrderStatusChoices.REFUNDED
        order.payment_status = PaymentStatusChoices.PAID
        order.save()

    def __set_is_returning_products(self, order: Order):
        products = [item['product'] for item in self.goods]
        order_items = OrderItem.objects.filter(product__in=products, order=order)
        order_items.update(is_returning=True)
