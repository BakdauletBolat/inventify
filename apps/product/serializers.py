from django.db.models import Count, Sum
from rest_framework import serializers

from apps.product.models import Product


class ProductImageSerializer(serializers.Serializer):
    image = serializers.ImageField()
    id = serializers.IntegerField()


class ProductSerializer(serializers.Serializer):
    id = serializers.IntegerField()
    name = serializers.CharField()
    sku = serializers.CharField()
    price = serializers.IntegerField(source='prices.last.cost')
    supplier_id = serializers.IntegerField()
    stock_count = serializers.SerializerMethodField()
    picture = serializers.ImageField(source='pictures.first.image', allow_null=True, default=None)
    pictures = ProductImageSerializer(many=True)

    @staticmethod
    def get_stock_count(obj: Product):
        stock_count = obj.stocks.aggregate(q=Sum("quantity", default=0))
        return stock_count['q']

