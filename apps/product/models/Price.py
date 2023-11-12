from django.db import models
from base.models import BaseModel


class Price(BaseModel):
    cost = models.IntegerField()
    quality = models.ForeignKey('stock.Quality', null=True, blank=True, on_delete=models.CASCADE)

    def __str__(self):
        return str(self.cost)

    class Meta:
        verbose_name = 'Цена'
        verbose_name_plural = 'Цены'