from apps.car.models.Model import ModelCar
from apps.car.models.ModificationDetails import *


class Modification(models.Model):
    default_fk_param = {
        "on_delete": models.CASCADE,
        "null": True,
        "blank": True
    }

    name = models.CharField(max_length=255, verbose_name='Наименование модификации')
    capacity = models.FloatField(default=0, verbose_name='Вместимость (объем мотора)', null=True, blank=True)
    power = models.IntegerField(default=0, verbose_name='Мощность', null=True, blank=True)
    numberOfCycle = models.IntegerField(default=0, verbose_name='Количество шин', null=True, blank=True)
    numberOfValves = models.IntegerField(default=0, verbose_name='Количество клапанов', null=True, blank=True)
    vinCode = models.IntegerField(default=0, verbose_name='Вин код', null=True, blank=True)
    axleConfiguration = models.ForeignKey(AxleConfiguration, verbose_name='Тип оси', **default_fk_param)
    bodyType = models.ForeignKey(BodyType, verbose_name='Тип кузова', **default_fk_param)
    driveType = models.ForeignKey(DriveType, verbose_name='Тип вождения(руль)', **default_fk_param)
    gearType = models.ForeignKey(GearType, verbose_name='Тип кпп', **default_fk_param)
    fuelType = models.ForeignKey(FuelType, verbose_name='Тип топлива', **default_fk_param)
    modelCar = models.ForeignKey(ModelCar, verbose_name='Модель машины', **default_fk_param)

    def __str__(self):
        return f"{self.id}"

    class Meta:
        verbose_name = 'Тех характиристика автомобиля (Модификации)'
        verbose_name_plural = 'Тех характиристики автомобиля (Модификации)'


class Engine(models.Model):
    name = models.CharField(max_length=255, verbose_name='Код')
    modification = models.ForeignKey(Modification, on_delete=models.CASCADE, null=True, blank=True,
                                     related_name='engine')

    def __str__(self):
        return self.name

    class Meta:
        verbose_name = 'Код двигателя'
        verbose_name_plural = 'Коды двигателя'
