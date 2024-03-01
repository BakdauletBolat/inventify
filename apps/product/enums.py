from django.db import models


class StatusChoices(models.IntegerChoices):
    RAW = 1, 'Необработан'
    IN_STOCK = 2, 'В наличии'
    RESERVED = 3, 'Зарезервирован'
    SOLD = 4, 'Продан'
    DELETED = 5, 'Удален'


class StatusChoicesRecar(models.IntegerChoices):
    not_parsed = 1
    in_stock = 2
    reserved = 3
    out_of_stock = 4
