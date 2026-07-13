from django.contrib.contenttypes.fields import GenericRelation
from django.db.models.signals import post_save
from django.dispatch import receiver
from eav.decorators import register_eav

from apps.car.models.Modification import Modification
from apps.car.models.ModificationDetails import *
from apps.category.models import Category
from apps.product.enums import StatusChoices
from base.models import BaseModel
from history.models.History import History
from history.services.create_history import create_history


@register_eav()
class Product(BaseModel):
    name = models.CharField(max_length=255, verbose_name='Наименование')
    code = models.ManyToManyField(OemCodes, null=True, blank=True)
    market_price = models.IntegerField(default=0, verbose_name='Рыночная цена', null=True, blank=True)

    modification = models.ForeignKey(Modification, blank=True, null=True, on_delete=models.SET_NULL)
    category = models.ForeignKey(Category, blank=True, null=True, on_delete=models.CASCADE, related_name='products')
    color = models.ForeignKey(ColorType, null=True, blank=True, on_delete=models.CASCADE)

    properties = models.CharField(max_length=255, verbose_name='Свойства', null=True, blank=True)
    defect = models.CharField(max_length=255, verbose_name='Дефект', null=True, blank=True)
    comment = models.TextField(verbose_name='Комментарий', null=True, blank=True)
    status = models.IntegerField(choices=StatusChoices.choices, default=StatusChoices.RAW.value)

    mileage = models.FloatField(null=True, blank=True)
    mileageType = models.ForeignKey(MileageType, verbose_name='Тип пробега', on_delete=models.SET_NULL, null=True,
                                    blank=True)
    parent = models.ForeignKey(
        'self', on_delete=models.CASCADE, null=True, blank=True, related_name='components'
    )

    histories = GenericRelation(History)

    from apps.stock.models import Warehouse
    warehouse = models.ForeignKey(Warehouse, on_delete=models.SET_NULL, null=True, blank=True, related_name='products')

    def __str__(self):
        return self.name

    class Meta:
        verbose_name = 'Продукт'
        verbose_name_plural = 'Продукты'


class ProductView(models.Model):
    product = models.OneToOneField(Product, on_delete=models.CASCADE, related_name="view_data")
    views_count = models.PositiveIntegerField(default=0)  # Количество просмотров

    def increment_product_view(self, product):
        """Увеличивает счетчик просмотров для продукта."""
        product_view, created = ProductView.objects.get_or_create(product=product)
        product_view.views_count += 1
        product_view.save()

    def __str__(self):
        return f"{self.product.name} - {self.views_count}"

    class Meta:
        verbose_name = 'Просмотр продукта'
        verbose_name_plural = 'Просмотры продукта'


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

    # Файл из хранилища удаляет django-cleanup (post_delete/при замене),
    # в том числе при удалении через queryset.delete()


#
@receiver(post_save, sender=Product)
def changed_product(sender, instance, **kwargs):
    if kwargs.get('update_fields') is None:
        create_history(sender=sender, instance=instance, type='single', **kwargs)


# Связанные ProductImage удаляются каскадом (on_delete=CASCADE),
# их файлы из хранилища удаляет django-cleanup по post_delete.
#
#
# @receiver(m2m_changed, sender=Product.prices.through)
# def changed_product_prices(sender, instance, **kwargs):
#     if kwargs.get('action') in ['post_add', 'post_remove']:
#         create_history(sender=sender, instance=instance, type='many_to_many', **kwargs)
