from django.db import models

from apps.category.models import Category
from apps.product.models import Product
from base import models as base_models
from handbook.models import City


class Quality(base_models.BaseModel):
    name = models.CharField(max_length=255)

    def __str__(self):
        return f"{self.id}: {self.name}"

    class Meta:
        verbose_name = 'Качество'
        verbose_name_plural = 'Качества'


class Warehouse(base_models.BaseModel):
    name = models.CharField(max_length=255)
    city = models.ForeignKey(City, on_delete=models.SET_NULL, null=True, blank=True)
    products_category = models.ManyToManyField(Category, null=True, blank=True)

    def __str__(self):
        return self.name

    class Meta:
        verbose_name = 'Склад'
        verbose_name_plural = 'Склады'


class Stock(base_models.BaseModel):
    product = models.ForeignKey(Product, on_delete=models.CASCADE, related_name='stocks')
    warehouse = models.ForeignKey(Warehouse, on_delete=models.CASCADE)
    quality = models.ForeignKey(Quality, on_delete=models.SET_NULL, null=True, blank=True)
    quantity = models.PositiveIntegerField(default=0)
    min_stock_level = models.PositiveIntegerField(default=10)

    class Meta:
        unique_together = ('product', 'quality', 'warehouse')
        verbose_name = 'Остаток'
        verbose_name_plural = 'Остатки'

    def __str__(self):
        return f"Продукт: {self.product} кол. ({self.quantity})"


class StockHistory(base_models.BaseModel):
    stock = models.ForeignKey(Stock, on_delete=models.CASCADE)
    quantity_before = models.PositiveIntegerField(null=True, blank=True)
    quantity_after = models.PositiveIntegerField()

    class Meta:
        verbose_name = 'История остатка'
        verbose_name_plural = 'История остатков'


class StockReceipt(base_models.BaseModel):
    product = models.ForeignKey(Product, on_delete=models.CASCADE)
    warehouse = models.ForeignKey(Warehouse, on_delete=models.CASCADE)
    quality = models.ForeignKey(Quality, on_delete=models.CASCADE)
    quantity = models.PositiveIntegerField()

    def __str__(self):
        return f"{self.quantity} единиц продукта {self.product.name} поступило на склад {self.warehouse.name}"

    class Meta:
        verbose_name = 'Приемка'
        verbose_name_plural = 'Приемка'

    def save(self, *args, **kwargs):
        # stock, created = Stock.objects.get_or_create(product=self.product, warehouse=self.warehouse,
        #                                              quality=self.quality)
        # stock.quantity += self.quantity
        # stock.save()
        # stock_history = StockHistory(
        #     stock=stock,
        #     quantity_before=stock.quantity,
        #     quantity_after=stock.quantity + self.quantity
        # )
        # stock_history.save()
        super(StockReceipt, self).save(*args, **kwargs)

    def delete(self, using=None, keep_parents=False):
        # stock, created = Stock.objects.get_or_create(product=self.product, warehouse=self.warehouse,
        #                                              quality=self.quality)
        # stock.quantity -= self.quantity
        # stock.save()
        super(StockReceipt, self).delete()
