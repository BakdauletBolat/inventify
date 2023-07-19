from rest_framework import serializers
from apps.order import models


class OrderItemSerializer(serializers.ModelSerializer):
    product_id = serializers.IntegerField(required=True)
    quantity = serializers.IntegerField(required=True)

    class Meta:
        fields = ('product_id', 'quantity', 'order_id')
        model = models.OrderItem


class OrderSerializer(serializers.ModelSerializer):
    uuid = serializers.UUIDField(read_only=True)
    goods = OrderItemSerializer(many=True)

    def create(self, validated_data):
        goods = validated_data.pop('goods', None)
        order = models.Order.objects.create(**validated_data)

        if goods:
            for good in goods:
                good['order_id'] = order.id
                models.OrderItem.objects.create(**good)
        return order

    class Meta:
        fields = ('uuid', 'goods')
        model = models.Order
