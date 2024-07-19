from django.db.models import IntegerChoices


class MovementEnum(IntegerChoices):
    IN = 1
    OUT = 2
