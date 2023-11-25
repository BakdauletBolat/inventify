from rest_framework import serializers

from apps.product.models import Product
from apps.product.models.Product import ProductImage
from apps.product.serializers import ProductDetailSerializer


class ProductImageDeSerializer(serializers.ModelSerializer):
    class Meta:
        model = ProductImage
        fields = '__all__'


class ProductDeSerializer(serializers.ModelSerializer):
    detail = ProductDetailSerializer()
    status = serializers.CharField(read_only=True)
    price = serializers.IntegerField(required=False, allow_null=True)

    class Meta:
        model = Product
        fields = '__all__'
        read_only_fields = ['pictures', 'modifications', 'market_price']
