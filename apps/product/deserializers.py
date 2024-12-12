from rest_framework import serializers

from apps.car.serializers import OemCodesCreateIfNotExistField
from apps.product.eav_serializer import ProductEAVSerializer
from apps.product.models import Product
from apps.product.models.Product import ProductImage
from apps.product.serializers import ProductDetailSerializer
from apps.stock.models import Warehouse


class ProductImageDeSerializer(serializers.ModelSerializer):
    image = serializers.ListField(
        child=serializers.ImageField(allow_empty_file=False, use_url=False),
        write_only=True
    )

    class Meta:
        model = ProductImage
        fields = '__all__'

    def create(self, validated_data):
        uploaded_images = validated_data.pop("image")
        product = validated_data.get("product")

        for image in uploaded_images:
            ProductImage.objects.create(product=product, image=image)

        return product


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
    warehouse_id = serializers.PrimaryKeyRelatedField(required=False, queryset=Warehouse.objects.all(),
                                                      source='warehouse')

    class Meta:
        model = Product
        exclude = ('modification',)
        read_only_fields = ['pictures', 'market_price', ]
