import time

from celery import shared_task

from apps.stock.actions import ImportWarehouseAction
from apps.stock.models import Stock
from base.requests import RecarRequest


@shared_task
def import_warehouse_detail():
    page = 1
    size = 50
    Stock.objects.all().delete()
    for pageNumber in range(page, 110, 1):
        warehouses = RecarRequest().get_warehouses(pageNumber, size)
        for warehouse in warehouses:
            ImportWarehouseAction().import_detail(warehouse['id'])


@shared_task
def import_warehouse():
    size = 50
    page = 1

    for pageNumber in range(page, 110, 1):
        warehouses = RecarRequest().get_warehouses(pageNumber, size)
        for warehouse in warehouses:
            ImportWarehouseAction().run(warehouse)


@shared_task
def import_warehouses_from_recar():
    import_warehouse.delay()
    time.sleep(300)
    import_warehouse_detail.delay()
