from django.db import models
from apps.product.models import Product
from base import models as base_models


class Quality(base_models.BaseModel):
    name = models.CharField(max_length=255)

    def __str__(self):
        return self.name


class Warehouse(models.Model):
    name = models.CharField(max_length=255)

    def __str__(self):
        return self.name


class Stock(models.Model):
    product = models.ForeignKey(Product, on_delete=models.CASCADE)
    quality = models.ForeignKey(Quality, on_delete=models.CASCADE)
    quantity = models.PositiveIntegerField(default=0)
    min_stock_level = models.PositiveIntegerField(default=10)

    def __str__(self):
        return f"{self.product} ({self.quantity})"
