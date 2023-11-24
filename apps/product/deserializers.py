from rest_framework import serializers

from apps.product.enums import StatusChoices
from apps.product.models import Product
from apps.product.serializers import ProductDetailSerializer


class ProductDeSerializer(serializers.ModelSerializer):
    detail = ProductDetailSerializer()
    status = serializers.ChoiceField(choices=StatusChoices.choices)
    price = serializers.IntegerField(required=False, allow_null=True)

    class Meta:
        model = Product
        fields = '__all__'
        read_only_fields = ['pictures', 'modifications', 'market_price']
