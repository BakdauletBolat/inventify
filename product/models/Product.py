from django.db import models
from product.models.Price import Price
from django.contrib.contenttypes.fields import GenericRelation
from history.models.History import History
from history.services.create_history import create_history
from django.dispatch import receiver
from django.db.models.signals import m2m_changed, pre_save


class Product(models.Model):
    name = models.CharField(max_length=255)
    prices = models.ManyToManyField(Price, related_name='products')
    histories = GenericRelation(History)

    def __str__(self):
        return self.name


@receiver(pre_save, sender=Product)
def changed_product(sender, instance, **kwargs):
    create_history(sender=sender, instance=instance, action='создание', type='single')


@receiver(m2m_changed, sender=Product.prices.through)
def changed_product_prices(sender, instance, **kwargs):
    create_history(sender=sender, instance=instance, action=kwargs.get('action'), type='many_to_many',
                   pk_set=kwargs.get('pk_set'))
