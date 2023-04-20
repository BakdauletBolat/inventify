from django.db import models
from base.models import BaseModel


class Price(BaseModel):
    cost = models.IntegerField()

    def __str__(self):
        return str(self.cost)
