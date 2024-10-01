from rest_framework.exceptions import ValidationError

from apps.stock.enums import MovementEnum


def update_quantity(stock, movement_type, quantity):
    if movement_type == MovementEnum.IN:
        stock.quantity += quantity
    elif movement_type == MovementEnum.OUT:
        if quantity > stock.quantity:
            raise ValidationError("Недостаточно товара на складе")
        stock.quantity -= quantity
    stock.save()
    return stock
