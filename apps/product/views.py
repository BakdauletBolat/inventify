from django.db.models import OuterRef, Subquery
from django_filters.rest_framework import DjangoFilterBackend
from drf_yasg.utils import swagger_auto_schema
from rest_framework import status
from rest_framework.generics import get_object_or_404
from rest_framework.parsers import MultiPartParser, FormParser
from rest_framework.response import Response
from rest_framework.viewsets import ModelViewSet

from apps.product import deserializers, serializers
from apps.product.actions import ProductAction
from apps.product.filters import DynamicProductFilterSet
from apps.product.models.Price import Price
from apps.product.models.Product import Product, ProductImage
from apps.product.serializers import AssignWarehouseSerializer
from base.paginations import CustomPageNumberPagination
from base.views import BaseAPIView
from inventify.permissions import IsStaff


class AdminProductImageView(BaseAPIView):
    parser_classes = (MultiPartParser, FormParser)
    deserializer_class = deserializers.ProductImageDeSerializer
    serializer_class = serializers.ProductImageSerializer
    queryset = ProductImage.objects.all()
    pagination_class = CustomPageNumberPagination
    permission_classes = [IsStaff]

    def post(self, request, *args, **kwargs):
        serializer = self.get_deserializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response(status=status.HTTP_201_CREATED)

    def delete(self, request, *args, **kwargs):
        instance = get_object_or_404(self.queryset, **kwargs)
        instance.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)


class AdminProductViewSetV2(ModelViewSet):
    deserializer_class = deserializers.ProductDeSerializerV2
    serializer_class = serializers.ProductSerializerV2
    queryset = Product.objects.prefetch_related('price',
                                                'pictures',
                                                'eav_values').select_related(
        'category', ).all().order_by('-created_at')
    filter_backends = [DjangoFilterBackend]
    filterset_class = DynamicProductFilterSet
    permission_classes = [IsStaff]

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
            self.get_queryset()
        )
        latest_price = Price.objects.filter(product=OuterRef('pk')).order_by('-created_at')
        queryset = queryset.annotate(latest_price=Subquery(latest_price.values('cost')[:1]))
        list_serializer = serializers.ProductListSerializerV2

        page = self.paginate_queryset(queryset)
        if page is not None:
            serializer = list_serializer(page, many=True, context={"request": request})
            return self.get_paginated_response(serializer.data)

        serializer = list_serializer(queryset, many=True, context={"request": request})
        return Response(serializer.data)

    @swagger_auto_schema(responses={200: serializers.ProductListSerializerV2, },
                         request_body=deserializer_class,
                         operation_id='Обновить',
                         tags=['Запчасть V2'],
                         )
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

    def add_component(self, request, *args, **kwargs):
        pass

    def remove_component(self, request, *args, **kwargs):
        pass


class ProductViewSet(ModelViewSet):
    deserializer_class = deserializers.ProductDeSerializerV2
    serializer_class = serializers.ProductSerializerV2
    queryset = Product.objects.prefetch_related('price',
                                                'pictures',
                                                ).select_related(
        'category', 'warehouse').all().order_by('-created_at')
    filter_backends = [DjangoFilterBackend]
    filterset_class = DynamicProductFilterSet

    def list(self, request, *args, **kwargs):
        queryset = self.filter_queryset(
            self.get_queryset()
        )
        latest_price = Price.objects.filter(product=OuterRef('pk')).order_by('-created_at')
        queryset = queryset.annotate(latest_price=Subquery(latest_price.values('cost')[:1]))
        list_serializer = serializers.ProductListSerializerV2

        page = self.paginate_queryset(queryset)
        if page is not None:
            serializer = list_serializer(page, many=True, context={"request": request})
            return self.get_paginated_response(serializer.data)

        serializer = list_serializer(queryset, many=True, context={"request": request})
        return Response(serializer.data)
