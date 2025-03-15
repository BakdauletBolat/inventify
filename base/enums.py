from django.db import models


class StatusEnum(models.IntegerChoices):
    ACTIVE = 1, 'Активный'
    DELETED = 2, 'Удален'
