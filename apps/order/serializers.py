from rest_framework import serializers

from apps.order import models
from apps.order.enums import PaymentTypeChoices, DeliveryTypeChoices
from apps.product.enums import StatusChoices
from apps.product.models import Product
from apps.product.serializers import ProductSerializer
from apps.stock.models import Quality, Warehouse
from apps.stock.serializers import QualitySerializer, WareHouseSerializer


class OrderItemSerializer(serializers.ModelSerializer):
    product_id = serializers.PrimaryKeyRelatedField(required=True,
                                                    queryset=Product.objects.filter(status=StatusChoices.IN_STOCK),
                                                    source='product',
                                                    write_only=True)
    product = ProductSerializer(read_only=True)
    # quality_id = serializers.PrimaryKeyRelatedField(required=True,
    #                                                 queryset=Quality.objects.all(),
    #                                                 source='quality',
    #                                                 write_only=True)
    quality = QualitySerializer(read_only=True)
    quantity = serializers.IntegerField(required=True)

    class Meta:
        exclude = ('order',)
        model = models.OrderItem


class OrderSerializer(serializers.ModelSerializer):
    uuid = serializers.UUIDField(read_only=True)
    goods = OrderItemSerializer(many=True)
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
    warehouse_id = serializers.PrimaryKeyRelatedField(required=True,
                                                      queryset=Warehouse.objects.all(),
                                                      source='warehouse',
                                                      write_only=True)
    warehouse = WareHouseSerializer(read_only=True)

    def create(self, validated_data):
        goods = validated_data.pop('goods', None)
        total = list(map(lambda x: getattr(x['product'].price.last(), 'cost', 0) * x['quantity'], goods))
        validated_data['total'] = sum(total)
        order = models.Order.objects.create(**validated_data)

        if goods:
            for good in goods:
                good['order_id'] = order.id
                models.OrderItem.objects.create(**good)
        return order

    class Meta:
        fields = '__all__'
        model = models.Order
