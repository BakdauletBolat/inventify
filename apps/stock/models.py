from django.db import models
from apps.product.models import Product
from base import models as base_models


class Quality(base_models.BaseModel):
    name = models.CharField(max_length=255)

    def __str__(self):
        return f"{self.id}: {self.name}"


class Warehouse(base_models.BaseModel):
    name = models.CharField(max_length=255)

    def __str__(self):
        return self.name


class Stock(base_models.BaseModel):
    product = models.ForeignKey(Product, on_delete=models.CASCADE, related_name='stocks')
    warehouse = models.ForeignKey(Warehouse, on_delete=models.CASCADE)
    quality = models.ForeignKey(Quality, on_delete=models.CASCADE)
    quantity = models.PositiveIntegerField(default=0)
    min_stock_level = models.PositiveIntegerField(default=10)

    class Meta:
        unique_together = ('product', 'quality', 'warehouse')

    def __str__(self):
        return f"Продукт: {self.product} кол. ({self.quantity})"


class StockHistory(base_models.BaseModel):
    stock = models.ForeignKey(Stock, on_delete=models.CASCADE)
    quantity_before = models.PositiveIntegerField(null=True, blank=True)
    quantity_after = models.PositiveIntegerField()


class StockReceipt(base_models.BaseModel):
    product = models.ForeignKey(Product, on_delete=models.CASCADE)
    warehouse = models.ForeignKey(Warehouse, on_delete=models.CASCADE)
    quality = models.ForeignKey(Quality, on_delete=models.CASCADE)
    quantity = models.PositiveIntegerField()

    def __str__(self):
        return f"{self.quantity} единиц продукта {self.product.name} поступило на склад {self.warehouse.name}"

    class Meta:
        verbose_name = 'Поступление'
        verbose_name_plural = 'Поступлений'

    def save(self, *args, **kwargs):
        stock, created = Stock.objects.get_or_create(product=self.product, warehouse=self.warehouse,
                                                     quality=self.quality)
        stock.quantity += self.quantity
        stock.save()
        stock_history = StockHistory(
            stock=stock,
            quantity_before=stock.quantity,
            quantity_after=stock.quantity + self.quantity
        )
        stock_history.save()
        super(StockReceipt, self).save(*args, **kwargs)

    def delete(self, using=None, keep_parents=False):
        stock, created = Stock.objects.get_or_create(product=self.product, warehouse=self.warehouse,
                                                     quality=self.quality)
        stock.quantity -= self.quantity
        stock.save()
        super(StockReceipt, self).delete()
