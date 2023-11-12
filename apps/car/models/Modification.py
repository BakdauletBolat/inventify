from django.db import models
from base import models as base_models
from apps.car.models.Model import ModelCar


class AxleConfiguration(models.Model):
    name = models.CharField(max_length=255, verbose_name='Наименование оси')

    def __str__(self):
        return self.name

    class Meta:
        verbose_name = 'Ось вращения'
        verbose_name_plural = 'Оси вращения'


class BodyType(models.Model):
    name = models.CharField(max_length=255, verbose_name='Наименование кузова')

    def __str__(self):
        return self.name

    class Meta:
        verbose_name = 'Тип кузова'
        verbose_name_plural = 'Типы кузова'


class ColorType(models.Model):
    name = models.CharField(max_length=255, verbose_name='Наименование расцветки')

    def __str__(self):
        return self.name

    class Meta:
        verbose_name = 'Расцветка машины'
        verbose_name_plural = 'Расцветка машины'


class DriveType(models.Model):
    name = models.CharField(max_length=255, verbose_name='Наименование типа вождения')

    def __str__(self):
        return self.name

    class Meta:
        verbose_name = 'Тип вождения'
        verbose_name_plural = 'Типы вождения'


class Engine(models.Model):
    name = models.CharField(max_length=255, verbose_name='Код')

    def __str__(self):
        return self.name

    class Meta:
        verbose_name = 'Код двигателя'
        verbose_name_plural = 'Коды двигателя'


class FuelType(models.Model):
    name = models.CharField(max_length=255, verbose_name='Наименование типа топлива')

    def __str__(self):
        return self.name

    class Meta:
        verbose_name = 'Тип топлива'
        verbose_name_plural = 'Типы топлива'


class GearType(models.Model):
    name = models.CharField(max_length=255, verbose_name='Наименование типа КПП')

    def __str__(self):
        return self.name

    class Meta:
        verbose_name = 'Тип КПП'
        verbose_name_plural = 'Типы КПП'


class ManufacturerType(models.Model):
    name = models.CharField(max_length=255, verbose_name='Наименование  производителя')

    def __str__(self):
        return self.name

    class Meta:
        verbose_name = 'Производитель'
        verbose_name_plural = 'Производитель'


class PlatformType(models.Model):
    name = models.CharField(max_length=255, verbose_name='Платформа')

    def __str__(self):
        return self.name

    class Meta:
        verbose_name = 'Платформа'
        verbose_name_plural = 'Платформа машины'


class SteeringType(models.Model):
    name = models.CharField(max_length=255, verbose_name='Наименование руля')

    def __str__(self):
        return self.name

    class Meta:
        verbose_name = 'Тип рулевого управления'
        verbose_name_plural = 'Типы рулевого управления'


class SuspensionType(models.Model):
    name = models.CharField(max_length=255, verbose_name='Наименование подвески')

    def __str__(self):
        return self.name

    class Meta:
        verbose_name = 'Тип подвески'
        verbose_name_plural = 'Типы подвесок'


class MileageType(models.Model):
    name = models.CharField(max_length=255, verbose_name='Наименование пробега')

    def __str__(self):
        return self.name

    class Meta:
        verbose_name = 'Тип пробега'
        verbose_name_plural = 'Типы пробега'


class Modification(base_models.BaseModel):
    name = models.CharField(max_length=255, verbose_name='Наименование модификации')
    capacity = models.IntegerField(default=0, verbose_name='Вместимость (объем мотора)')
    power = models.IntegerField(default=0, verbose_name='Мощность')
    numberOfCycle = models.IntegerField(default=0, verbose_name='Количество шин')
    numberOfValves = models.IntegerField(default=0, verbose_name='Количество клапанов')
    vinCode = models.IntegerField(default=0, verbose_name='Вин код')
    axleConfiguration = models.ForeignKey(AxleConfiguration,
                                          verbose_name='Тип оси',
                                          on_delete=models.CASCADE,
                                          null=True,
                                          blank=True)
    bodyType = models.ForeignKey(BodyType,
                                 verbose_name='Тип кузова',
                                 on_delete=models.CASCADE,
                                 null=True,
                                 blank=True)
    engine = models.ForeignKey(Engine,
                               verbose_name='Тип двигателя',
                               on_delete=models.CASCADE,
                               null=True,
                               blank=True)
    gearType = models.ForeignKey(GearType,
                                 verbose_name='Тип кпп',
                                 on_delete=models.CASCADE,
                                 null=True,
                                 blank=True)
    fuelType = models.ForeignKey(FuelType,
                                 verbose_name='Тип топлива',
                                 on_delete=models.CASCADE,
                                 null=True,
                                 blank=True)
    mileageType = models.ForeignKey(MileageType,
                                    verbose_name='Тип пробега',
                                    on_delete=models.CASCADE,
                                    null=True,
                                    blank=True)
    modelCar = models.ForeignKey(ModelCar,
                                 verbose_name='Модель машины',
                                 on_delete=models.CASCADE,
                                 null=True,
                                 blank=True
                                 )

    def __str__(self):
        return

    class Meta:
        verbose_name = 'Тип кузова'
        verbose_name_plural = 'Типы кузова'
