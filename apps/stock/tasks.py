import time

from celery import shared_task

from apps.stock.actions import ImportWarehouseAction
from base.requests import RecarRequest


@shared_task
def import_warehouse_detail():
    page = 1
    size = 70

    for pageNumber in range(page, 80, 1):
        warehouses = RecarRequest().get_warehouses(pageNumber, size)
        for warehouse in warehouses:
            ImportWarehouseAction().import_detail(warehouse['id'])


@shared_task
def import_warehouse():
    page = 1
    size = 50

    for pageNumber in range(1, 100, 1):
        warehouses = RecarRequest().get_warehouses(pageNumber, size)
        for warehouse in warehouses:
            ImportWarehouseAction().run(warehouse)


@shared_task
def import_warehouses_from_recar():
    import_warehouse.delay()
    time.sleep(600)
    import_warehouse_detail.delay()
