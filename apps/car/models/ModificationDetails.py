from django.db import models


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
