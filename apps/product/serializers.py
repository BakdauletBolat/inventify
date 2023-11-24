from rest_framework import serializers

from apps.car.serializers import ModificationSerializer
from apps.product.models.Product import *


class ProductDetailSerializer(serializers.ModelSerializer):
    class Meta:
        model = ProductDetail
        exclude = ('product',)


class ProductImageSerializer(serializers.Serializer):
    class Meta:
        model = ProductImage
        fields = '__all__'


class ProductSerializer(serializers.ModelSerializer):
    price = serializers.SerializerMethodField()
    warehouse = serializers.CharField(read_only=True)
    modification = ModificationSerializer()
    detail = ProductDetailSerializer()
    status = serializers.CharField(source='get_status_display')


    @staticmethod
    def get_price(obj):
        return getattr(obj.price.last(), 'cost', None)

    class Meta:
        model = Product
        fields = '__all__'
        read_only_fields = ['pictures', 'warehouse']
