from apps.car.models.ModificationDetails import *


class ModificationDraft(models.Model):
    product_id = models.IntegerField('Product ID')
    data = models.JSONField()

    def __str__(self):
        return f"{self.product_id}"

    class Meta:
        verbose_name = 'Импортированные данные о модификации'
        verbose_name_plural = 'Импортированные данные о модификации'
