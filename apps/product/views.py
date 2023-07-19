from rest_framework import viewsets
from apps.product.models.Product import Product
from apps.product import serializers


class ProductViewSet(viewsets.ModelViewSet):
    queryset = Product.objects.all()
    serializer_class = serializers.ProductSerializer

