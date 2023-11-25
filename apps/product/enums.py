from django.db import models


class StatusChoices(models.IntegerChoices):
    RAW = 1, 'Необработан'
    IN_STOCK = 2, 'В наличии'
    RESERVED = 3, 'Зарезервирован'
    SOLD = 4, 'Продан'
    DELETED = 5, 'Удален'
