from django.db import models
from django.utils.translation import gettext as _
from handbook.models import City


class Address(models.Model):
    address = models.CharField('Адрес', max_length=255)
    street = models.CharField('Улица', max_length=255, null=True, blank=True)
    apartment = models.CharField('Квартира', max_length=255, null=True, blank=True)
    building = models.CharField('Дом', max_length=255, null=True, blank=True)
    coords = models.JSONField('Кордината', max_length=255, null=True, blank=True)
    city = models.ForeignKey(City, null=True, blank=True, on_delete=models.CASCADE, related_name='addresses')
    user = models.ForeignKey('User', on_delete=models.CASCADE, related_name='addresses', null=True, blank=True)

    def __str__(self):
        return self.address

    class Meta:
        verbose_name = _('Адрес')
        verbose_name_plural = _('Адрес')