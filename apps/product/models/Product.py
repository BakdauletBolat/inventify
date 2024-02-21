from django.contrib.contenttypes.fields import GenericRelation

from apps.car.models.Modification import Modification
from apps.car.models.ModificationDetails import *
from apps.category.models import Category
from apps.product.enums import StatusChoices
from base.models import BaseModel
from history.models.History import History


class Product(BaseModel):
    name = models.CharField(max_length=255, verbose_name='Наименование')
    code = models.ManyToManyField(OemCodes, null=True, blank=True)
    market_price = models.IntegerField(default=0, verbose_name='Рыночная цена', null=True, blank=True)

    warehouse = models.ForeignKey('stock.Warehouse', blank=True, null=True, on_delete=models.SET_NULL)
    modification = models.ForeignKey(Modification, blank=True, null=True, on_delete=models.SET_NULL)
    category = models.ManyToManyField(Category, blank=True, null=True)
    color = models.ForeignKey(ColorType, null=True, blank=True, on_delete=models.CASCADE)

    properties = models.CharField(max_length=255, verbose_name='Свойства', null=True, blank=True)
    defect = models.CharField(max_length=255, verbose_name='Дефект', null=True, blank=True)
    comment = models.TextField(verbose_name='Комментарий', null=True, blank=True)
    status = models.IntegerField(choices=StatusChoices.choices, default=StatusChoices.RAW.value)

    mileage = models.FloatField(null=True, blank=True)
    mileageType = models.ForeignKey(MileageType, verbose_name='Тип пробега', on_delete=models.SET_NULL, null=True,
                                    blank=True)

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
    product = models.OneToOneField(Product, verbose_name='Продукт', on_delete=models.CASCADE, related_name='detail')

    class Meta:
        verbose_name = 'Детали продукта'
        verbose_name_plural = 'Детали продукта'

    def __str__(self):
        return self.product.name


class ProductImage(models.Model):
    image = models.ImageField(upload_to='ProductImage/')
    product = models.ForeignKey(Product, on_delete=models.CASCADE, related_name='pictures')

    def __str__(self):
        return self.product.name

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
