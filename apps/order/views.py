from django.core import exceptions
from django.db import transaction
from django.utils.translation import gettext as _
from rest_framework import status, generics, viewsets
from rest_framework.exceptions import ValidationError, MethodNotAllowed
from rest_framework.response import Response

from apps.order import models, serializers
from apps.order.enums import PaymentStatusChoices, OrderStatusChoices


class OrderViewSet(viewsets.ModelViewSet):
    queryset = models.Order.objects.all()
    serializer_class = serializers.OrderSerializer

    @transaction.atomic
    def create(self, request, *args, **kwargs):
        try:
            return super().create(request, *args, **kwargs)
        except exceptions.ValidationError as e:
            return Response({'detail': e.message}, status=status.HTTP_422_UNPROCESSABLE_ENTITY)

    @transaction.atomic
    def destroy(self, request, *args, **kwargs):
        instance = self.get_object()
        if instance.status == OrderStatusChoices.COMPLETED:
            raise ValidationError(_('Вы не можете удалить проведенный заказ'))
        instance.status = OrderStatusChoices.CANCELED
        instance.payment_status = PaymentStatusChoices.FAILED
        instance.save()
        return Response(status=status.HTTP_204_NO_CONTENT)

    def update(self, request, *args, **kwargs):
        raise MethodNotAllowed(method='PATCH')


class OrderConfirmView(generics.GenericAPIView):
    queryset = models.Order.objects.filter(status=OrderStatusChoices.PROCESSING)
    serializer_class = serializers.OrderSerializer

    def post(self, request, *args, **kwargs):
        instance = self.get_object()
        instance.update_order_status_success()
        serializer = self.get_serializer(instance)
        return Response(serializer.data)
