from django.db import models

from base import models as base_models
from apps.product.models import Product


class Feedback(base_models.BaseModel):
    phone = models.CharField(max_length=255, verbose_name='Номер телефона')
    name = models.CharField(max_length=255, verbose_name='Имя')
    product = models.ForeignKey(Product, on_delete=models.SET_NULL, blank=True, null=True, verbose_name='Продукт', related_name='feedbacks')
    comment = models.TextField(blank=True, null=True, verbose_name='Комментарий')
    completed_at = models.DateTimeField(auto_now_add=False, blank=True, null=True)

    class Meta:
        verbose_name = 'Обратная связь'
        verbose_name_plural = 'Обратные связи'
