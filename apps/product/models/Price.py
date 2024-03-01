from django.db import models

from apps.product.models.Product import Product
from base.models import BaseModel


class Price(BaseModel):
    cost = models.IntegerField(default=0, null=True, blank=True)
    product = models.ForeignKey(Product, on_delete=models.SET_NULL, related_name='price',
                                verbose_name='Цена', null=True, blank=True)

    def __str__(self):
        return str(self.cost)

    class Meta:
        verbose_name = 'Цена'
        verbose_name_plural = 'Цены'
