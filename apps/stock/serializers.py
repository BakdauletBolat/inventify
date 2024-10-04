from rest_framework import serializers

from apps.category.models import Category
from apps.category.serializers import CategorySerializer
from apps.product import serializers as product_serializers
from apps.product.enums import StatusChoices
from apps.stock import models
from handbook.models import City
from handbook.serializers import CitySerializer


class QualitySerializer(serializers.ModelSerializer):
    class Meta:
        model = models.Quality
        fields = ('id', 'name')


class WareHouseSerializer(serializers.ModelSerializer):
    category_ids = serializers.ListField(child=serializers.IntegerField(), write_only=True, required=False,
                                         source='products_category', allow_null=True, allow_empty=True, default=[])
    categories = CategorySerializer(many=True, source='products_category', read_only=True)
    city = CitySerializer(read_only=True)
    city_id = serializers.PrimaryKeyRelatedField(queryset=City.objects.all(), write_only=True, source='city')

    class Meta:
        model = models.Warehouse
        fields = ('id', 'name', 'categories', 'category_ids', 'city', 'city_id', 'min_stock_level')

    def create(self, validated_data):
        category_ids = validated_data.pop('products_category', [])

        # Создаем объект склада без категории
        warehouse = models.Warehouse.objects.create(**validated_data)

        # Если указаны категории, добавляем их к складу
        if category_ids:
            categories = Category.objects.filter(id__in=category_ids)
            warehouse.products_category.set(categories)

        return warehouse


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


class MoveProductSerializer(serializers.Serializer):
    product_id = serializers.PrimaryKeyRelatedField(
        queryset=models.Product.objects.filter(
            status__in=[StatusChoices.RAW,
                        StatusChoices.IN_STOCK]),
        source='product')
    source_warehouse_id = serializers.PrimaryKeyRelatedField(queryset=models.Warehouse.objects.all(),
                                                             source='source_warehouse')
    dest_warehouse_id = serializers.PrimaryKeyRelatedField(queryset=models.Warehouse.objects.all(),
                                                           source='dest_warehouse')
    quantity = serializers.IntegerField(allow_null=True, default=1, required=False)
    quality_id = serializers.IntegerField(required=False, allow_null=True, source='quality')

    def validate(self, attrs):
        """
        Общая проверка данных.
        1. Убедитесь, что source_warehouse_id и dest_warehouse_id различаются.
        2. Проверка ограничения по максимальному количеству продуктов на складе.
        3. Проверка соответствия категории продукта с допустимыми категориями на складе.
        """

        source_warehouse: models.Warehouse = attrs['source_warehouse']
        dest_warehouse: models.Warehouse = attrs['dest_warehouse']
        product: models.Product = attrs['product']
        quantity = attrs['quantity']
        categories = []

        for category in dest_warehouse.products_category.all():
            categories.extend(category.get_all_descendants())

        if source_warehouse == dest_warehouse:
            raise serializers.ValidationError("Склад отправления и склад назначения должны быть разными.")

        # Проверка ограничения по максимальному количеству продуктов на складе
        if (dest_warehouse.get_stock() + quantity) > dest_warehouse.min_stock_level:
            raise serializers.ValidationError(
                f"Превышение максимального лимита склада. Максимально допустимое количество: {dest_warehouse.min_stock_level}"
            )

        # if product.category not in categories:
        #     raise serializers.ValidationError(
        #         f"Продукт категории '{product.category}' не может быть размещен на этом складе."
        #     )

        return attrs
