from django.db import models
from apps.product.models.Price import Price
from django.contrib.contenttypes.fields import GenericRelation

from apps.supplier.models import Supplier
from history.models.History import History
from history.services.create_history import create_history
from django.dispatch import receiver
from django.db.models.signals import m2m_changed, post_save


class Product(models.Model):
    name = models.CharField(max_length=255)
    sku = models.CharField(max_length=255)
    supplier = models.ForeignKey(Supplier, on_delete=models.CASCADE)
    prices = models.ManyToManyField(Price, related_name='products')
    histories = GenericRelation(History)

    def __str__(self):
        return self.name

    class Meta:
        unique_together = ['supplier', 'sku']


class ProductImage(models.Model):
    image = models.ImageField(upload_to='ProductImage/')
    product = models.ForeignKey(Product, on_delete=models.CASCADE, related_name='pictures')


@receiver(post_save, sender=Product)
def changed_product(sender, instance, **kwargs):
    if kwargs.get('update_fields') is not None:
        create_history(sender=sender, instance=instance, type='single', **kwargs)


@receiver(m2m_changed, sender=Product.prices.through)
def changed_product_prices(sender, instance, **kwargs):
    if kwargs.get('action') in ['post_add', 'post_remove']:
        create_history(sender=sender, instance=instance, type='many_to_many', **kwargs)
