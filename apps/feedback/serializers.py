from rest_framework import serializers

from apps.feedback.models import Feedback
from apps.product.models import Product


class ProductBasicSerializer(serializers.ModelSerializer):
    category_name = serializers.CharField(source='category.name', read_only=True)
    modification_name = serializers.CharField(source='modification.name', read_only=True)

    class Meta:
        model = Product
        fields = ['id', 'name', 'category_name', 'modification_name', 'status', 'market_price']
        read_only_fields = fields


class FeedbackSerializer(serializers.ModelSerializer):
    product_detail = ProductBasicSerializer(source='product', read_only=True)

    class Meta:
        model = Feedback
        fields = '__all__'
