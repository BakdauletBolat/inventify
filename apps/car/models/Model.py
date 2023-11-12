from django.db import models

from apps.car.models.Modification import ManufacturerType


class ModelCar(models.Model):
    name = models.CharField(max_length=255, verbose_name='Наименование модели')
    manufacturer = models.ForeignKey(ManufacturerType, on_delete=models.CASCADE, verbose_name='Производитель')
    startDate = models.DateField(auto_created=False)
    endDate = models.DateField(auto_created=False)

    def __str__(self):
        return self.name

    class Meta:
        verbose_name = 'Производитель'
        verbose_name_plural = 'Производитель'
