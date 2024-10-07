from django_filters.rest_framework import DjangoFilterBackend
from drf_yasg.utils import swagger_auto_schema
from rest_framework import viewsets, status
from rest_framework.response import Response

from apps.stock import models, serializers
from apps.stock.actions import StockAction
from apps.stock.filters import WarehouseFilter


class WareHouseViewSet(viewsets.ModelViewSet):
    queryset = models.Warehouse.objects.all()
    serializer_class = serializers.WareHouseSerializer
    filter_backends = [DjangoFilterBackend]
    filterset_class = WarehouseFilter

    def retrieve(self, request, *args, **kwargs):
        instance = self.get_object()
        serializer = self.get_serializer(instance)
        return Response(serializer.data)


class MoveProductViewSet(viewsets.ViewSet):

    @swagger_auto_schema(request_body=serializers.MoveProductSerializer)
    def move(self, request, *args, **kwargs):
        serializer = serializers.MoveProductSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        movements = StockAction().move_product(**serializer.validated_data)

        return Response({
            'movements': [
                {'movement_id': movements[0].id, 'movement_type': 'OUT'},
                {'movement_id': movements[1].id, 'movement_type': 'IN'}
            ]
        }, status=status.HTTP_200_OK)
