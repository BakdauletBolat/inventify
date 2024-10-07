from rest_framework import serializers

from apps.car.serializers import OemCodesCreateIfNotExistField
from apps.product.eav_serializer import ProductEAVSerializer
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
    code = OemCodesCreateIfNotExistField(required=False, allow_null=True)

    class Meta:
        model = Product
        fields = '__all__'
        read_only_fields = ['pictures', 'modifications', 'market_price']


class ProductDeSerializerV2(serializers.ModelSerializer):
    detail = ProductDetailSerializer(required=False, allow_null=True)
    status = serializers.CharField(read_only=True)
    price = serializers.IntegerField(required=False, allow_null=True)
    code = OemCodesCreateIfNotExistField(required=False, allow_null=True)
    eav_attributes = ProductEAVSerializer(required=False, allow_null=True)

    class Meta:
        model = Product
        exclude = ('modification',)
        read_only_fields = ['pictures', 'market_price', 'name', ]
