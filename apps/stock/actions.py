from apps.stock.models import Warehouse


class ImportWarehouseAction:

    @staticmethod
    def run(warehouse_data):
        warehouse, created = Warehouse.objects.update_or_create(
            id=warehouse_data['id'],
            defaults={
                'name': warehouse_data['name'],
                'min_stock_level': warehouse_data.get('partsSpace', 10)
            }
        )

        category_ids = [category['id'] for category in warehouse_data['partCategories']]
        warehouse.products_category.set(category_ids)
