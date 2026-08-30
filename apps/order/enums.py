from django.db import models


class PaymentTypeChoices(models.IntegerChoices):
    CASH = 1, 'Наличные'
    INTERNET_PAYMENT = 2, 'Интернет оплата'
    PREPAID = 3, 'Предоплата'


class DeliveryTypeChoices(models.IntegerChoices):
    PICKUP = 1, 'Самовывоз'
    TRANSPORT = 2, 'Перевозка'


class PaymentStatusChoices(models.IntegerChoices):
    PENDING = 1, 'В ожидании'
    PAID = 2, 'Оплачен'
    FAILED = 3, 'Отклонен'


class OrderStatusChoices(models.IntegerChoices):
    PROCESSING = 1, 'В процессе'
    COMPLETED = 2, 'Завершен'
    CANCELED = 3, 'Отменен'
    REFUNDED = 4, 'Возвращен'
    DELETED = 5, 'Удален'


# Статусы и типы оплаты приходят из Recar строками, и их набор пополняется на
# стороне Recar. Раньше здесь были IntegerChoices, и неизвестное значение
# роняло импорт заказа целиком (KeyError: 'processing'), поэтому теперь это
# обычные словари с безопасным разбором в RecarOrderMapping.
RECAR_ORDER_STATUS_MAP = {
    'ready': OrderStatusChoices.PROCESSING,
    'processing': OrderStatusChoices.PROCESSING,
    'done': OrderStatusChoices.COMPLETED,
    'declined': OrderStatusChoices.CANCELED,
}

RECAR_PAYMENT_TYPE_MAP = {
    'cash': PaymentTypeChoices.CASH,
    'bank': PaymentTypeChoices.INTERNET_PAYMENT,
    'prepaid': PaymentTypeChoices.PREPAID,
}
