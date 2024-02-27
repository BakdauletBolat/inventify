import uuid

from django.core.exceptions import ValidationError
from django.utils.translation import gettext as _

from apps.order.enums import *
from apps.product.models import Product
from apps.stock.models import Quality, Stock, Warehouse
from base import models as base_models


def default_uuid():
    return uuid.uuid4()


class Order(base_models.BaseModel):
    total = models.DecimalField(max_digits=10, decimal_places=2)
    uuid = models.UUIDField(unique=True, default=default_uuid, blank=True)
    payment_type = models.IntegerField(choices=PaymentTypeChoices.choices, default=PaymentTypeChoices.CASH)
    delivery_type = models.IntegerField(choices=DeliveryTypeChoices.choices, default=DeliveryTypeChoices.PICKUP)
    comment = models.TextField(null=True, blank=True)
    discount = models.IntegerField(default=0)
    warehouse = models.ForeignKey(Warehouse, on_delete=models.CASCADE)
    client = models.CharField(default='', null=True, blank=True, max_length=255)
    status = models.IntegerField(choices=OrderStatusChoices.choices, default=OrderStatusChoices.PROCESSING)
    payment_status = models.IntegerField(choices=PaymentStatusChoices.choices, default=PaymentStatusChoices.PENDING)

    def update_payment_success(self):
        self.payment_status = PaymentStatusChoices.PAID
        self.save()

    def update_payment_failure(self):
        self.payment_status = PaymentStatusChoices.FAILED
        self.save()

    def update_order_status_success(self):
        if self.payment_status == PaymentStatusChoices.PAID \
                and self.payment_type == PaymentTypeChoices.INTERNET_PAYMENT:
            self.status = OrderStatusChoices.COMPLETED

        elif self.payment_type == PaymentTypeChoices.CASH:
            self.status = OrderStatusChoices.COMPLETED
            self.update_payment_success()

        else:
            raise ValidationError(_('Заказ не оплачен, либо отклонен'))
        self.save()

    def update_order_status_cancel(self):
        self.status = OrderStatusChoices.CANCELED
        self.save()

    class Meta:
        verbose_name = _('Заказ')
        verbose_name_plural = _('Заказы')

    def __str__(self):
        return f"{self.client} - {self.warehouse.name}"


class OrderItem(models.Model):
    product = models.ForeignKey(Product, on_delete=models.CASCADE)
    quantity = models.PositiveIntegerField()
    order = models.ForeignKey(Order, on_delete=models.CASCADE, related_name='goods')
    quality = models.ForeignKey(Quality, on_delete=models.CASCADE)

    def clean(self):
        stock = Stock.objects.filter(product=self.product, quality=self.quality).last()
        if stock is None:
            raise ValidationError(f"_(Нету остатков товара: {self.product.name}")
        if stock.quantity - self.quantity < 0:
            raise ValidationError(f"Не хватает товара текущее кол: {stock.quantity}")

    def save(self, *args, **kwargs):
        # self.clean()
        # stocks = Stock.objects.filter(product=self.product, quality_id=self.quality.id)
        # stock = stocks.last()
        # stock_history = StockHistory(
        #     stock=stock,
        #     quantity_before=stock.quantity,
        #     quantity_after=stock.quantity - self.quantity
        # )
        # stock_history.save()
        # stock.quantity -= self.quantity
        # stock.save()
        super(OrderItem, self).save(*args, **kwargs)

    class Meta:
        verbose_name = _('Деталь заказа')
        verbose_name_plural = _('Детали заказа')
