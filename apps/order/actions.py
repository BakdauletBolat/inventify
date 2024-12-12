from django.db.utils import DataError

from apps.order.enums import *
from apps.order.models import Order, OrderItem


class ImportOrderAction:
    def run(self, order_data: dict):

        order = Order(
            id=order_data['id'],
            payment_type=PaymentTypeChoicesRecar.__getitem__(name=order_data['paymentType']),
            payment_status=PaymentStatusChoices.PAID if order_data['paymentCompleted'] else PaymentStatusChoices.FAILED,
            status=
            OrderStatusChoicesRecar.__getitem__(name=order_data['status'])
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
