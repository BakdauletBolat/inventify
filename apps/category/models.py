from django.db import models

from base.models import BaseModel


# Create your models here.

class Category(BaseModel):
    name = models.CharField(max_length=255)
    parent = models.ForeignKey('self', on_delete=models.SET_NULL, null=True, blank=True, related_name='children')
    recar_category_id = models.IntegerField(null=True, blank=True, verbose_name='Категория из Рекар')


    def __str__(self):
        return self.name

    def get_all_descendants(self):
        """Получить все дочерние категории, включая саму категорию."""
        descendants = [self]
        children = list(self.children.all())
        for child in children:
            descendants.extend(child.get_all_descendants())
        return descendants

    class Meta:
        verbose_name = 'Категория'
        verbose_name_plural = 'Категории'