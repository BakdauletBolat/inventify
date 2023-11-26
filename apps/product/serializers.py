from rest_framework import serializers

from apps.car.serializers import ModificationSerializer
from apps.product.models.Product import *


class ProductDetailSerializer(serializers.ModelSerializer):
    class Meta:
        model = ProductDetail
        exclude = ('product',)


class ProductImageSerializer(serializers.ModelSerializer):
    image = serializers.SerializerMethodField()

    class Meta:
        model = ProductImage
        fields = '__all__'

    def get_image(self, instance):
        request = self.context.get('request')
        image = instance.image.url
        return request.build_absolute_uri(image)


class ProductSerializer(serializers.ModelSerializer):
    price = serializers.SerializerMethodField()
    warehouse = serializers.CharField(read_only=True)
    modification = ModificationSerializer()
    detail = ProductDetailSerializer()
    status = serializers.CharField(source='get_status_display')
    pictures = serializers.SerializerMethodField()

    @staticmethod
    def get_price(obj):
        return getattr(obj.price.last(), 'cost', None)

    def get_pictures(self, obj):
        return ProductImageSerializer(obj.pictures.all(), many=True, context=self.context).data

    class Meta:
        model = Product
        fields = '__all__'
        read_only_fields = ['pictures', 'warehouse']
