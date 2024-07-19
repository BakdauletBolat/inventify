from rest_framework import serializers

from apps.category.serializers import CategorySerializer
from apps.product import serializers as product_serializers
from apps.stock import models


class QualitySerializer(serializers.ModelSerializer):
    class Meta:
        model = models.Quality
        fields = ('id', 'name')


class WareHouseSerializer(serializers.ModelSerializer):
    category_ids = serializers.ListField(child=serializers.IntegerField(), write_only=True, required=False,
                                         source='products_category')
    categories = CategorySerializer(many=True, source='products_category', read_only=True)

    class Meta:
        model = models.Warehouse
        fields = ('id', 'name', 'categories', 'category_ids')


class StockReceiptSerializer(serializers.ModelSerializer):
    product = product_serializers.ProductSerializer(read_only=True)
    product_id = serializers.IntegerField(write_only=True)
    warehouse = WareHouseSerializer(read_only=True)
    warehouse_id = serializers.IntegerField(write_only=True)
    quality = QualitySerializer(read_only=True)
    quality_id = serializers.IntegerField(write_only=True)

    class Meta:
        model = models.StockMovement
        fields = ('id', 'product', 'warehouse', 'quality', 'quantity',
                  'product_id', 'warehouse_id', 'quality_id')
