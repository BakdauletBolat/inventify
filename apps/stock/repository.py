from apps.stock.models import Stock, StockMovement
from base.repository import BaseRepository


class StockRepository(BaseRepository):
    model = Stock

    def get_or_create_stock(self, product, warehouse, quality=None):
        stock, created = self.model.objects.get_or_create(
            product=product,
            warehouse=warehouse,
            defaults={
                'quantity': 0,
                'quality': quality
            },
        )
        return stock


class StockMovementRepository(BaseRepository):
    model = StockMovement

    def create(self, product, warehouse, movement_type, quantity, quality=None):
        movement = self.model.objects.create(
            product=product,
            warehouse=warehouse,
            movement_type=movement_type,
            quantity=quantity,
            quality=quality
        )

        # Сохраняем движение
        movement.save()

        return movement
