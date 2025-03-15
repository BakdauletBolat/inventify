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


class OrderStatusChoicesRecar(models.IntegerChoices):
    ready = 1
    done = 2
    declined = 3


class PaymentTypeChoicesRecar(models.IntegerChoices):
    cash = 1,
    bank = 2
    prepaid = 3
