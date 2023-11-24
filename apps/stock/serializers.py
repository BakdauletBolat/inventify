from rest_framework import serializers

from apps.product import serializers as product_serializers
from apps.stock import models


class QualitySerializer(serializers.ModelSerializer):
    class Meta:
        model = models.Quality
        fields = ('id', 'name')


class WareHouseSerializer(serializers.ModelSerializer):
    class Meta:
        model = models.Warehouse
        fields = ('id', 'name',)


class StockReceiptSerializer(serializers.ModelSerializer):
    product = product_serializers.ProductSerializer(read_only=True)
    product_id = serializers.IntegerField(write_only=True)
    warehouse = WareHouseSerializer(read_only=True)
    warehouse_id = serializers.IntegerField(write_only=True)
    quality = QualitySerializer(read_only=True)
    quality_id = serializers.IntegerField(write_only=True)

    class Meta:
        model = models.StockReceipt
        fields = ('id', 'product', 'warehouse', 'quality', 'quantity',
                  'product_id', 'warehouse_id', 'quality_id')
