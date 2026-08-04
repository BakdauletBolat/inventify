from django.db import models


class ImportProductData(models.Model):
    product_id = models.IntegerField('Product ID', db_index=True)
    data = models.JSONField()
    # null=True — у строк, созданных до появления полей, даты неизвестны
    created_at = models.DateTimeField('Создан', auto_now_add=True, null=True)
    updated_at = models.DateTimeField('Обновлён', auto_now=True, null=True)

    def __str__(self):
        return f"{self.product_id}"

    class Meta:
        verbose_name = 'Импротированные данные о продукте'
        verbose_name_plural = 'Импротированные данные о продукте'
