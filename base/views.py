from dateutil.utils import today
from rest_framework.response import Response
from rest_framework.views import APIView

from apps.order.enums import OrderStatusChoices
from apps.order.models import Order
from apps.product.repository import ProductRepository


# Create your views here.
class BaseAPIView(APIView):
    deserializer_class = None
    serializer_class = None
    pagination_class = None

    def get_deserializer(self, *args, **kwargs):
        return self.deserializer_class(*args, **kwargs)

    def get_serializer(self, *args, **kwargs):
        return self.serializer_class(*args, **kwargs)

    def get_pagination(self, *args, **kwargs):
        return self.pagination_class(*args, **kwargs)


class DashBoardView(APIView):
    def get(self, request, *args, **kwargs):
        parts_count = ProductRepository.get_in_stock().count()
        orders_count = Order.objects.count()
        orders_inprogress_count = Order.objects.filter(status=OrderStatusChoices.PROCESSING).count()
        sale_for_today = Order.objects.filter(created_at__date=today().date()).count()

        return Response({
            "parts_count": parts_count,
            "orders_count": orders_count,
            "orders_inprogress_count": orders_inprogress_count,
            "sale_for_today": sale_for_today
        })
