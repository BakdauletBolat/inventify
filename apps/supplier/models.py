from django.db import models
from base.models import BaseModel


# Create your models here.

class Supplier(BaseModel):
    name = models.CharField(max_length=255)

    def __str__(self):
        return self.name
