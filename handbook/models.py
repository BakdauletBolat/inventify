from django.conf import settings
from django.db import models

from base import models as base_models

User = settings.AUTH_USER_MODEL


class Country(models.Model):
    name = models.CharField(max_length=255)
    uid = models.CharField(max_length=255)

    def __str__(self) -> str:
        return self.name

    class Meta:
        verbose_name = 'Страна'
        verbose_name_plural = 'Страна'


class City(base_models.BaseModel):
    name = models.CharField(max_length=255)
    uid = models.CharField(max_length=255)
    country = models.ForeignKey(Country, on_delete=models.CASCADE)

    def __str__(self) -> str:
        return self.name

    class Meta:
        verbose_name = 'Город'
        verbose_name_plural = 'Города'


class Address(models.Model):
    address = models.CharField('Адрес', max_length=255)
    address1 = models.CharField('Адрес Доп', max_length=255, null=True, blank=True)
    street = models.CharField('Улица', max_length=255, null=True, blank=True)
    apartment = models.CharField('Квартира', max_length=255, null=True, blank=True)
    floor = models.CharField('Этаж', max_length=255, null=True, blank=True)
    entrance = models.CharField('Подъезд', max_length=255, null=True, blank=True)
    building = models.CharField('Дом', max_length=255, null=True, blank=True)
    coords = models.JSONField('Кордината', max_length=255, null=True, blank=True)
    city = models.ForeignKey(City, null=True, blank=True, on_delete=models.CASCADE, related_name='addresses')
    user = models.ForeignKey(User, null=True, blank=True, on_delete=models.CASCADE, related_name='addresses')

    def __str__(self):
        return self.address

    class Meta:
        verbose_name = 'Адрес'
        verbose_name_plural = 'Адрес'
