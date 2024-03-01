from apps.stock.models import Warehouse


class ImportWarehouseAction:

    @staticmethod
    def run(warehouse_data):
        warehouse = Warehouse.objects.create(
            id=warehouse_data['id'],
            name=warehouse_data['name']
        )
        category_ids = [category['id'] for category in warehouse_data['partCategories']]
        warehouse.products_category.set(category_ids)
