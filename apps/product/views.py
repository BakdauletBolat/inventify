from rest_framework import status
from rest_framework.generics import get_object_or_404
from rest_framework.parsers import MultiPartParser, FormParser
from rest_framework.response import Response

from apps.product import deserializers
from apps.product import serializers
from apps.product.actions import CreateProductAction, UpdateProductAction
from apps.product.deserializers import ProductImageDeSerializer
from apps.product.models.Product import Product, ProductImage
from apps.product.repository import ProductRepository
from apps.product.serializers import ProductImageSerializer
from base.paginations import CustomPageNumberPagination
from base.views import BaseAPIView


class ProductViewSet(BaseAPIView):
    queryset = Product.objects.all()
    deserializer_class = deserializers.ProductDeSerializer
    serializer_class = serializers.ProductSerializer
    pagination_class = CustomPageNumberPagination

    def post(self, request, *args, **kwargs):
        serializer = self.get_deserializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        product = CreateProductAction(serializer.validated_data).run()
        return Response(self.serializer_class(product).data, status=status.HTTP_201_CREATED)

    def get(self, request, *args, **kwargs):
        if kwargs.get('pk', None) is None:
            pagination = self.get_pagination()
            page = pagination.paginate_queryset(self.queryset.all(), request)
            serializer = self.get_serializer(page, many=True, context={"request": request})
            return pagination.get_paginated_response(serializer.data)

        instance = get_object_or_404(self.queryset, **kwargs)
        serializer = self.get_serializer(instance, context={"request": request})
        return Response(serializer.data, status=status.HTTP_200_OK)

    def patch(self, request, *args, **kwargs):
        serializer = self.get_deserializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        instance = get_object_or_404(self.queryset, **kwargs)
        product = UpdateProductAction(serializer.validated_data).run(instance)
        return Response(self.serializer_class(product).data, status=status.HTTP_200_OK)

    def delete(self, request, *args, **kwargs):
        instance = get_object_or_404(self.queryset, **kwargs)
        ProductRepository.delete(instance)
        return Response(status=status.HTTP_204_NO_CONTENT)


class ProductImageView(BaseAPIView):
    parser_classes = (MultiPartParser, FormParser)
    deserializer_class = ProductImageDeSerializer
    serializer_class = ProductImageSerializer
    queryset = ProductImage.objects.all()

    def post(self, request, *args, **kwargs):
        serializer = self.get_deserializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response(status=status.HTTP_201_CREATED)

    def delete(self, request, *args, **kwargs):
        instance = get_object_or_404(self.queryset, **kwargs)
        instance.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)
