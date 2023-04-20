from django.db import models
from base.models import BaseModel


# Create your models here.

class Category(BaseModel):
    name = models.CharField(max_length=255)
    parent = models.ForeignKey('self', on_delete=models.DO_NOTHING, null=True, blank=True)

    def __str__(self):
        return self.name
