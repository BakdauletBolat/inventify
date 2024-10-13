from rest_framework import serializers

from apps.car.serializers import OemCodesCreateIfNotExistField
from apps.product.eav_serializer import ProductEAVSerializer
from apps.product.models import Product
from apps.product.models.Product import ProductImage
from apps.product.serializers import ProductDetailSerializer
from apps.stock.models import Warehouse


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
    status = serializers.IntegerField(required=False, allow_null=True)
    price = serializers.IntegerField(required=False, allow_null=True)
    code = OemCodesCreateIfNotExistField(required=False, allow_null=True)
    eav_attributes = ProductEAVSerializer(required=False, allow_null=True)
    name = serializers.CharField(required=False, allow_null=True, allow_blank=True)
    warehouse_id = serializers.PrimaryKeyRelatedField(queryset=Warehouse.objects.all(), source='warehouse')

    class Meta:
        model = Product
        exclude = ('modification',)
        read_only_fields = ['pictures', 'market_price', ]
