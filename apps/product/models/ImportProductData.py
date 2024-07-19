from django.db import models


class ImportProductData(models.Model):
    product_id = models.IntegerField('Product ID')
    data = models.JSONField()

    def __str__(self):
        return f"{self.product_id}"

    class Meta:
        verbose_name = 'Импротированные данные о продукте'
        verbose_name_plural = 'Импротированные данные о продукте'