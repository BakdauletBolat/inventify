from django.conf import settings
from django.db import models

from base import models as base_models

User = settings.AUTH_USER_MODEL


class Country(models.Model):
    name = models.CharField(max_length=255)
    uid = models.CharField(max_length=255, null=True, blank=True)

    def __str__(self) -> str:
        return self.name

    class Meta:
        verbose_name = 'Страна'
        verbose_name_plural = 'Страна'


class City(base_models.BaseModel):
    name = models.CharField(max_length=255)
    uid = models.CharField(max_length=255, null=True, blank=True)
    country = models.ForeignKey(Country, on_delete=models.CASCADE)

    def __str__(self) -> str:
        return self.name

    class Meta:
        verbose_name = 'Город'
        verbose_name_plural = 'Города'