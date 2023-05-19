from django.core.exceptions import ValidationError
from django.db import models

from apps.product.models import Product
from apps.stock.models import StockHistory, Stock
from base import models as base_models
import uuid





def default_uuid():
    return uuid.uuid4()


class Order(base_models.BaseModel):
    uuid = models.UUIDField(unique=True, default=default_uuid, blank=True)


class OrderItem(models.Model):
    product = models.ForeignKey(Product, on_delete=models.CASCADE)
    quantity = models.PositiveIntegerField()
    order = models.ForeignKey(Order, on_delete=models.CASCADE, related_name='goods')

    def clean(self):
        stock = Stock.objects.filter(product=self.product, quality_id=1).last()
        if stock is not None:
            if stock.quantity - self.quantity < 0:
                raise ValidationError(f"Не хватает товара текущая кол: {stock.quantity}")

    def save(self, *args, **kwargs):
        self.clean()
        stocks = Stock.objects.filter(product=self.product, quality_id=1)
        stock = stocks.last()
        stock_history = StockHistory(
            stock=stock,
            quantity_before=stock.quantity,
            quantity_after=stock.quantity - self.quantity
        )
        stock_history.save()
        stock.quantity -= self.quantity
        stock.save()
        super(OrderItem, self).save(*args, **kwargs)
