import uuid

from django.core.exceptions import ValidationError
from django.utils.translation import gettext as _

from apps.address.models import Address
from apps.order.enums import *
from apps.product.enums import StatusChoices
from apps.product.models import Product
from apps.stock.models import Stock, Warehouse
from base import models as base_models
from users.models.User import User


def default_uuid():
    return uuid.uuid4()


class Order(base_models.BaseModel):
    total = models.DecimalField(max_digits=10, decimal_places=2)
    uuid = models.UUIDField(unique=True, default=default_uuid, blank=True)
    payment_type = models.IntegerField(choices=PaymentTypeChoices.choices, default=PaymentTypeChoices.CASH)
    delivery_type = models.IntegerField(choices=DeliveryTypeChoices.choices, default=DeliveryTypeChoices.PICKUP)
    address = models.ForeignKey(Address, related_name='orders', on_delete=models.SET_NULL,
                                null=True, blank=True, verbose_name='Адрес доставки')
    comment = models.TextField(null=True, blank=True)
    discount = models.IntegerField(default=0)
    warehouse = models.ForeignKey(Warehouse, on_delete=models.SET_NULL, null=True, blank=True)
    client = models.CharField(default='', null=True, blank=True, max_length=255)
    user = models.ForeignKey(User, null=True, blank=True, on_delete=models.CASCADE)
    refund_order = models.ForeignKey('self', null=True, blank=True, related_name='refunds', on_delete=models.CASCADE)

    # Поля для данных клиента
    first_name = models.CharField('Имя', max_length=255, null=True, blank=True)
    last_name = models.CharField('Фамилия', max_length=255, null=True, blank=True)
    phone_number = models.CharField('Номер телефона', max_length=20, null=True, blank=True)
    email = models.EmailField('Email', max_length=255, null=True, blank=True)

    status = models.IntegerField(choices=OrderStatusChoices.choices, default=OrderStatusChoices.PROCESSING)
    payment_status = models.IntegerField(choices=PaymentStatusChoices.choices, default=PaymentStatusChoices.PENDING)

    class Meta:
        verbose_name = _('Заказ')
        verbose_name_plural = _('Заказы')

    def __str__(self):
        return f"{self.id}"


class OrderItem(models.Model):
    product = models.ForeignKey(Product, on_delete=models.CASCADE, related_name='order_item')
    quantity = models.PositiveIntegerField(default=1)
    order = models.ForeignKey(Order, on_delete=models.CASCADE, related_name='goods')
    is_returning = models.BooleanField(default=False)

    def clean(self):
        stock = Stock.objects.filter(product=self.product).last()
        if stock is None:
            raise ValidationError(f"_(Нету остатков товара: {self.product.name}")
        if stock.quantity - self.quantity < 0:
            raise ValidationError(f"Не хватает товара текущее кол: {stock.quantity}")

    def save(self, *args, **kwargs):
        super(OrderItem, self).save(*args, **kwargs)

    class Meta:
        verbose_name = _('Деталь заказа')
        verbose_name_plural = _('Детали заказа')

    @property
    def product_status(self):
        return StatusChoices(self.product.status).label


class ImportOrderData(models.Model):
    data = models.JSONField()

    def __str__(self):
        return f"{self.id}"

    class Meta:
        verbose_name = 'Импротированные заказы'
        verbose_name_plural = 'Импротированные заказы'
