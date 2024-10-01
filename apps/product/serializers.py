from rest_framework import serializers

from apps.car.serializers import ModificationSerializer, ModelCarSerializer
from apps.category.serializers import CategorySerializer
from apps.product.eav_serializer import ProductEAVSerializer
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
    color = serializers.CharField(read_only=True)
    category = CategorySerializer(read_only=True)
    code = serializers.StringRelatedField(read_only=True,
                                          many=True
                                          )
    modification = ModificationSerializer()
    warehouse = serializers.SerializerMethodField()
    detail = ProductDetailSerializer()
    status = serializers.CharField(source='get_status_display')
    pictures = serializers.SerializerMethodField()

    @staticmethod
    def get_price(obj):
        return getattr(obj.price.last(), 'cost', None)

    def get_pictures(self, obj: Product):
        return ProductImageSerializer(obj.pictures.all(), many=True, context=self.context).data

    @staticmethod
    def get_warehouse(obj: Product):
        from apps.stock.serializers import WareHouseSerializer
        if obj.stock.exists():
            return WareHouseSerializer(obj.stock.filter(quantity__gt=0).first().warehouse).data
        return None

    class Meta:
        model = Product
        fields = '__all__'
        read_only_fields = ['pictures', 'warehouse']


class ProductSerializerV2(ProductSerializer):
    eav_attributes = ProductEAVSerializer(source='*')
    modification = None

    class Meta(ProductSerializer.Meta):
        fields = '__all__'

    def get_pictures(self, obj: Product):
        return ProductImageSerializer(obj.pictures.all(), many=True, context=self.context).data


class ProductListSerializerV2(ProductSerializer):
    modelCar = serializers.SerializerMethodField('get_modelCar')

    class Meta(ProductSerializer.Meta):
        fields = ('id', 'name', 'category', 'pictures', 'modelCar', 'status', 'price', 'created_at')

    def get_pictures(self, obj: Product):
        return ProductImageSerializer(obj.pictures.all(), many=True, context=self.context).data

    @staticmethod
    def get_price(obj):
        return obj.latest_price

    @staticmethod
    def get_modelCar(obj: Product):
        return ModelCarSerializer(obj.eav.modelCar).data


class AssignWarehouseSerializer(serializers.Serializer):
    from apps.stock.models import Warehouse

    product_id = serializers.PrimaryKeyRelatedField(queryset=Product.objects.all(), source='product')
    warehouse_id = serializers.PrimaryKeyRelatedField(queryset=Warehouse.objects.all(), source='warehouse')
