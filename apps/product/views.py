from django.db.models import OuterRef, Subquery, Prefetch
from django_filters.rest_framework import DjangoFilterBackend
from drf_yasg.utils import swagger_auto_schema
from rest_framework import status
from rest_framework.generics import get_object_or_404
from rest_framework.parsers import MultiPartParser, FormParser
from rest_framework.response import Response
from rest_framework.viewsets import ModelViewSet

from apps.product import deserializers, serializers
from apps.product.actions import ProductAction
from apps.product.filters import DynamicProductFilterSet, ProductFilters
from apps.product.models.Price import Price
from apps.product.models.Product import Product, ProductImage
from apps.product.repository import ProductRepository
from apps.product.serializers import AssignWarehouseSerializer
from base.paginations import CustomPageNumberPagination
from base.views import BaseAPIView


class ProductViewSet(BaseAPIView):
    queryset = Product.objects.all()
    deserializer_class = deserializers.ProductDeSerializer
    serializer_class = serializers.ProductSerializer
    pagination_class = CustomPageNumberPagination
    filter_backends = [DjangoFilterBackend]
    filterset_class = ProductFilters

    def post(self, request, *args, **kwargs):
        serializer = self.get_deserializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        product = ProductAction().create(serializer.validated_data)
        return Response(self.serializer_class(product).data, status=status.HTTP_201_CREATED)

    def get(self, request, *args, **kwargs):
        if kwargs.get('pk', None) is None:
            self.queryset = self.filterset_class(request.GET, self.queryset.all()).qs
            pagination = self.get_pagination()
            page = pagination.paginate_queryset(self.queryset, request)
            serializer = self.get_serializer(page, many=True, context={"request": request})
            return pagination.get_paginated_response(serializer.data)

        instance = get_object_or_404(self.queryset, **kwargs)
        serializer = self.get_serializer(instance, context={"request": request})
        return Response(serializer.data, status=status.HTTP_200_OK)

    def patch(self, request, *args, **kwargs):
        serializer = self.get_deserializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        instance = get_object_or_404(self.queryset, **kwargs)
        product = ProductAction().update(instance, serializer.validated_data)
        return Response(self.serializer_class(product).data, status=status.HTTP_200_OK)

    def delete(self, request, *args, **kwargs):
        instance = get_object_or_404(self.queryset, **kwargs)
        ProductRepository.delete(instance)
        return Response(status=status.HTTP_204_NO_CONTENT)


class ProductImageView(BaseAPIView):
    parser_classes = (MultiPartParser, FormParser)
    deserializer_class = deserializers.ProductImageDeSerializer
    serializer_class = serializers.ProductImageSerializer
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


class ProductViewSetV2(ModelViewSet):
    deserializer_class = deserializers.ProductDeSerializerV2
    serializer_class = serializers.ProductSerializerV2
    queryset = Product.objects.prefetch_related('price', 'pictures').select_related(
        'category', ).all()
    filter_backends = [DjangoFilterBackend]
    filterset_class = DynamicProductFilterSet

    @swagger_auto_schema(request_body=deserializer_class(),
                         responses={201: serializer_class},
                         operation_id='Создание',
                         tags=['Запчасть V2'],
                         )
    def create(self, request, *args, **kwargs):
        deserializer = self.deserializer_class(data=request.data)
        deserializer.is_valid(raise_exception=True)
        product = ProductAction().create(deserializer.validated_data)
        return Response(data=self.get_serializer(product, context={"request": request}).data)

    @swagger_auto_schema(responses={200: serializers.ProductListSerializerV2},
                         operation_id='Список',
                         tags=['Запчасть V2'],
                         )
    def list(self, request, *args, **kwargs):
        queryset = self.filter_queryset(
            self.get_queryset().select_related(
                ).prefetch_related(
                'price',
                Prefetch('modification'),
                Prefetch('pictures'),
            ))
        latest_price = Price.objects.filter(product=OuterRef('pk')).order_by('-created_at')
        queryset = queryset.annotate(latest_price=Subquery(latest_price.values('cost')[:1]))
        list_serializer = serializers.ProductListSerializerV2

        page = self.paginate_queryset(queryset)
        if page is not None:
            serializer = list_serializer(page, many=True, context={"request": request})
            return self.get_paginated_response(serializer.data)

        serializer = list_serializer(queryset, many=True, context={"request": request})
        return Response(serializer.data)

    def update(self, request, *args, **kwargs):
        serializer = self.deserializer_class(data=request.data)
        serializer.is_valid(raise_exception=True)
        instance = get_object_or_404(self.queryset, **kwargs)
        product = ProductAction().update(instance, serializer.validated_data)
        return Response(self.get_serializer(product).data, status=status.HTTP_200_OK)

    def assign_warehouse(self, request, *args, **kwargs):
        serializer = AssignWarehouseSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        ProductAction().assign_to_warehouse(serializer.validated_data['product'],
                                            serializer.validated_data['warehouse'])
        return Response(status=status.HTTP_204_NO_CONTENT)
