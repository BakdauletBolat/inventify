from django.db import models


class ManufacturerType(models.Model):
    name = models.CharField(max_length=255, verbose_name='Наименование  производителя')
    image = models.ImageField(upload_to='Manufacturers/', blank=True, null=True)

    def __str__(self):
        return self.name

    class Meta:
        verbose_name = 'Производитель'
        verbose_name_plural = 'Производитель'


class ModelCar(models.Model):
    name = models.CharField(max_length=255, verbose_name='Наименование модели')
    manufacturer = models.ForeignKey(ManufacturerType, on_delete=models.CASCADE, verbose_name='Производитель')
    startDate = models.DateField(auto_created=False, null=True, blank=True)
    endDate = models.DateField(auto_created=False, null=True, blank=True)

    def __str__(self):
        return self.name

    class Meta:
        verbose_name = 'Модель автомобиля'
        verbose_name_plural = 'Модель автомобиля'
