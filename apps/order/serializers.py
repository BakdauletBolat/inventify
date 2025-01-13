from django.core.exceptions import ValidationError
from django.utils.translation import gettext as _
from rest_framework import serializers

from apps.order import models
from apps.order.enums import PaymentTypeChoices, DeliveryTypeChoices, PaymentStatusChoices, OrderStatusChoices
from apps.product.enums import StatusChoices
from apps.product.models import Product
from apps.product.serializers import ProductSerializer
from apps.stock.models import Warehouse
from apps.stock.serializers import QualitySerializer, WareHouseSerializer


class OrderItemSerializer(serializers.ModelSerializer):
    product_id = serializers.PrimaryKeyRelatedField(required=True,
                                                    queryset=Product.objects.filter(status=StatusChoices.IN_STOCK),
                                                    source='product',
                                                    write_only=True)
    product = ProductSerializer(read_only=True)
    quality = QualitySerializer(read_only=True)
    quantity = serializers.IntegerField(required=True)

    class Meta:
        exclude = ('order',)
        model = models.OrderItem

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Динамически обновляем queryset на основе контекста
        if self.context.get('refund_mode', False):
            self.fields['product_id'].queryset = Product.objects.filter(status=StatusChoices.SOLD)
        else:
            self.fields['product_id'].queryset = Product.objects.filter(status=StatusChoices.IN_STOCK)


class OrderSerializer(serializers.ModelSerializer):
    uuid = serializers.UUIDField(read_only=True)
    goods = OrderItemSerializer(many=True, required=True)
    total = serializers.DecimalField(read_only=True, max_digits=10, decimal_places=2)
    delivery_type_id = serializers.ChoiceField(write_only=True,
                                               choices=DeliveryTypeChoices.choices,
                                               source='delivery_type')
    delivery_type = serializers.CharField(read_only=True, source='get_delivery_type_display')
    payment_type_id = serializers.ChoiceField(write_only=True,
                                              choices=PaymentTypeChoices.choices,
                                              source='payment_type')
    payment_type = serializers.CharField(read_only=True, source='get_payment_type_display')
    payment_status = serializers.CharField(read_only=True, source='get_payment_status_display')

    status = serializers.CharField(read_only=True, source='get_status_display')
    warehouse_id = serializers.PrimaryKeyRelatedField(required=False,
                                                      queryset=Warehouse.objects.all(),
                                                      source='warehouse',
                                                      allow_null=True)
    warehouse = WareHouseSerializer(read_only=True)

    class Meta:
        fields = '__all__'
        model = models.Order


class OrderUpdateSerializer(OrderSerializer):
    payment_status = serializers.ChoiceField(choices=PaymentStatusChoices.choices, required=False)
    delivery_type_id = serializers.ChoiceField(required=False,
                                               choices=DeliveryTypeChoices.choices,
                                               source='delivery_type')

    payment_type_id = serializers.ChoiceField(required=False,
                                              choices=PaymentTypeChoices.choices,
                                              source='payment_type')
    warehouse_id = serializers.PrimaryKeyRelatedField(required=False,
                                                      queryset=Warehouse.objects.all(),
                                                      source='warehouse',
                                                      allow_null=True)

    class Meta(OrderSerializer.Meta):
        fields = (
            'payment_type_id',
            'delivery_type_id',
            'warehouse_id',
            'comment',
            'payment_status'
        )

    def validate(self, attrs):
        order_status = attrs.get('status', None)
        payment_status = attrs.get('payment_status', None)
        if order_status == OrderStatusChoices.COMPLETED and payment_status != PaymentStatusChoices.PAID:
            raise ValidationError(_('Для завершения заказа, оплатите сумму'))

        return attrs


class OrderRefundSerializer(serializers.ModelSerializer):
    warehouse_id = serializers.PrimaryKeyRelatedField(required=False,
                                                      queryset=Warehouse.objects.all(),
                                                      source='warehouse',
                                                      allow_null=True)
    goods = OrderItemSerializer(many=True, context={'refund_mode': True})
    refund_order_id = serializers.PrimaryKeyRelatedField(required=True,
                                                         queryset=models.Order.objects.all(),
                                                         source='refund_order',
                                                         allow_null=False)

    class Meta:
        fields = ('warehouse_id', 'comment', 'goods', 'refund_order_id')
        model = models.Order
