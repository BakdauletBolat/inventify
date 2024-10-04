from django.db import models
from django.db.models import Sum

from apps.category.models import Category
from apps.product.enums import StatusChoices
from apps.product.models import Product
from apps.stock.enums import MovementEnum
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
    min_stock_level = models.PositiveIntegerField(default=0, null=True)

    def __str__(self):
        return self.name

    def get_stock(self):
        return self.stock_set.filter(
            product__status=StatusChoices.IN_STOCK).aggregate(
            sum_product=Sum('quantity', default=0)
        )['sum_product']

    class Meta:
        verbose_name = 'Склад'
        verbose_name_plural = 'Склады'


class Stock(base_models.BaseModel):
    product = models.ForeignKey(Product, on_delete=models.CASCADE, related_name='stock')
    warehouse = models.ForeignKey(Warehouse, on_delete=models.CASCADE, null=True, blank=True)
    quality = models.ForeignKey(Quality, on_delete=models.SET_NULL, null=True, blank=True)
    quantity = models.PositiveIntegerField(default=0)

    class Meta:
        verbose_name = 'Остаток'
        verbose_name_plural = 'Остатки'

    def __str__(self):
        return f"Продукт: {self.product} кол. ({self.quantity})"


class StockMovement(base_models.BaseModel):
    product = models.ForeignKey(Product, on_delete=models.CASCADE)
    warehouse = models.ForeignKey(Warehouse, on_delete=models.CASCADE)
    movement_type = models.IntegerField('Тип движения', choices=MovementEnum.choices)
    quality = models.ForeignKey(Quality, on_delete=models.SET_NULL, null=True, blank=True)
    quantity = models.PositiveIntegerField()

    def __str__(self):
        if self.movement_type == MovementEnum.IN:
            movement = 'поступление на склада'
        else:
            movement = 'отгрузка со склада'
        return f"{self.quantity} единиц продукта {self.product.name} {movement} {self.warehouse.name} - {self.created_at}"

    class Meta:
        ordering = ('-created_at', )
        verbose_name = 'Движение остатков'
        verbose_name_plural = 'Движение остатков'

    def save(self, *args, **kwargs):
        super(StockMovement, self).save(*args, **kwargs)

    def delete(self, using=None, keep_parents=False):
        super(StockMovement, self).delete()


class WarehouseDrafts(models.Model):
    warehouse_id = models.IntegerField()
    data = models.JSONField()

    class Meta:
        verbose_name = 'Импортированные данные со склада'
        verbose_name_plural = 'Импортированные данные со склада'
