from django.db import models


class StatusChoices(models.IntegerChoices):
    RAW = 1, 'Необработан'
    IN_STOCK = 2, 'В наличии'
    RESERVED = 3, 'Зарезервирован'
    DELETED = 4, 'Удален'
    SOLD = 5, 'Продан'


class StatusChoicesRecar(models.IntegerChoices):
    not_parsed = 1
    in_stock = 2
    reserved = 3
    deleted = 4
    sold = 5