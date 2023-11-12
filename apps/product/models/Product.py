from django.contrib.contenttypes.fields import GenericRelation
from django.db import models
from django.db.models.signals import m2m_changed, post_save
from django.dispatch import receiver

from history.models.History import History
from history.services.create_history import create_history


class Product(models.Model):
    name = models.CharField(max_length=255, verbose_name='Наименование')
    code = models.CharField(max_length=255, verbose_name='Код')
    histories = GenericRelation(History)

    def __str__(self):
        return self.name

    class Meta:
        verbose_name = 'Продукт'
        verbose_name_plural = 'Продукты'


class ProductDetail(models.Model):
    height = models.FloatField(verbose_name='Высота', null=True, blank=True)
    width = models.FloatField(verbose_name='Ширина', null=True, blank=True)
    length = models.FloatField(verbose_name='Длина', null=True, blank=True)
    weight = models.FloatField(verbose_name='Вес', null=True, blank=True)
    product = models.ForeignKey(Product, verbose_name='Продукт', on_delete=models.CASCADE)

    class Meta:
        verbose_name = 'Детлаи продукта'
        verbose_name_plural = 'Детлаи продукта'

    def __str__(self):
        return self.product.name


class ProductImage(models.Model):
    image = models.ImageField(upload_to='ProductImage/')
    product = models.ForeignKey(Product, on_delete=models.CASCADE, related_name='pictures')

    class Meta:
        verbose_name = 'Фото продукта'
        verbose_name_plural = 'Фото продуктов'

#
# @receiver(post_save, sender=Product)
# def changed_product(sender, instance, **kwargs):
#     if kwargs.get('update_fields') is not None:
#         create_history(sender=sender, instance=instance, type='single', **kwargs)
#
#
# @receiver(m2m_changed, sender=Product.prices.through)
# def changed_product_prices(sender, instance, **kwargs):
#     if kwargs.get('action') in ['post_add', 'post_remove']:
#         create_history(sender=sender, instance=instance, type='many_to_many', **kwargs)
