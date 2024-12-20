from django.db import transaction
from django.utils.translation import gettext as _
from rest_framework import status, generics, viewsets
from rest_framework.decorators import action
from rest_framework.exceptions import ValidationError
from rest_framework.response import Response

from apps.order import models, serializers
from apps.order.actions import OrderAction
from apps.order.enums import OrderStatusChoices


class OrderViewSet(viewsets.ModelViewSet):
    queryset = models.Order.objects.all()
    serializer_class = serializers.OrderSerializer

    @transaction.atomic
    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        with transaction.atomic():
            order = OrderAction(serializer.validated_data).create()

        return Response(self.serializer_class(order).data, status=status.HTTP_201_CREATED)

    @transaction.atomic
    def destroy(self, request, *args, **kwargs):
        instance = self.get_object()
        if instance.status != OrderStatusChoices.PROCESSING:
            raise ValidationError(_('Вы не можете удалить проведенный заказ'))

        with transaction.atomic():
            OrderAction().delete(instance)
        return Response(status=status.HTTP_204_NO_CONTENT)

    def update(self, request, *args, **kwargs):
        with transaction.atomic():
            partial = kwargs.pop('partial', False)
            instance = self.get_object()
            serializer = serializers.OrderUpdateSerializer(instance, data=request.data, partial=partial)
            serializer.is_valid(raise_exception=True)
            self.perform_update(serializer)

            if getattr(instance, '_prefetched_objects_cache', None):
                instance._prefetched_objects_cache = {}

            return Response(self.serializer_class(instance).data)

    @action(detail=False, methods=['post'], url_path='refund')
    def refund(self, request, *args, **kwargs):
        serializer = serializers.OrderRefundSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        data = serializer.validated_data
        if data['refund_order'].status != OrderStatusChoices.COMPLETED:
            raise ValidationError(_('Вы не можете вернуть заказ, который не завершен'))
        with transaction.atomic():
            order = OrderAction(data).refund()
            return Response(self.serializer_class(order).data)


class OrderConfirmView(generics.GenericAPIView):
    queryset = models.Order.objects.filter(status=OrderStatusChoices.PROCESSING)
    serializer_class = serializers.OrderSerializer

    def post(self, request, *args, **kwargs):
        instance = self.get_object()
        order = OrderAction().confirm(instance)
        return Response(self.serializer_class(order).data)
