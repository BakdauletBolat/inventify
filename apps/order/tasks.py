import time

from celery import shared_task

from apps.order.actions import ImportOrderAction
from apps.order.models import ImportOrderData, Order
from base.requests import RecarRequest


@shared_task
def create_orders_draft():
    orders_recar = RecarRequest().get_orders()
    order_ids = list(map(lambda x: int(x['id']), orders_recar))
    orders = ImportOrderData.objects.filter(id__in=order_ids)
    difference_orders = set(order_ids).difference(orders.values_list('id', flat=True))
    for order_id in difference_orders:
        import_order_draft.delay(order_id)


@shared_task
def import_order_draft(order_id: int):
    request = RecarRequest()
    order_data = request.get_order(order_id)
    ImportOrderData.objects.create(id=order_id, data=order_data)


@shared_task
def import_order_task(id: int):
    order = ImportOrderData.objects.get(id=id)
    ImportOrderAction().run(order.data)


@shared_task
def create_orders():
    order_ids_recar = ImportOrderData.objects.values_list('id', flat=True)
    orders = Order.objects.filter(id__in=order_ids_recar).values_list('id', flat=True)
    difference_order_ids = set(order_ids_recar).difference(orders)
    batch_size = 100

    for start in range(0, len(difference_order_ids), batch_size):
        end = start + batch_size
        batch_ids = list(difference_order_ids)[start:end]
        remains_recar_orders = ImportOrderData.objects.filter(id__in=batch_ids)

        for order in remains_recar_orders:
            import_order_task.delay(order.id)


@shared_task
def import_orders_from_recar():
    create_orders_draft()
    time.sleep(300)
    create_orders()
