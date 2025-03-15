from django_filters.rest_framework import DjangoFilterBackend
from drf_yasg.utils import swagger_auto_schema
from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.response import Response

from apps.stock import models, serializers
from apps.stock.actions import StockAction
from apps.stock.filters import WarehouseFilter
from base.enums import StatusEnum
from base.paginations import CustomPageNumberPagination


class WareHouseViewSet(viewsets.ModelViewSet):
    queryset = models.Warehouse.objects.all()
    serializer_class = serializers.WareHouseSerializer
    filter_backends = [DjangoFilterBackend]
    filterset_class = WarehouseFilter
    pagination_class = CustomPageNumberPagination

    def retrieve(self, request, *args, **kwargs):
        instance = self.get_object()
        serializer = serializers.WarehouseDetailSerializer(instance, context={"request": request})
        return Response(serializer.data)

    @action(detail=False, methods=['delete'], url_path='bulk-delete')
    def bulk_delete(self, request):
        warehouse_ids = request.data.get("ids", [])
        warehouses = models.Warehouse.objects.filter(id__in=warehouse_ids, status=StatusEnum.ACTIVE.value)
        if warehouses.exists() is False:
            return Response({"error": "Не переданы ID складов или удалены"}, status=status.HTTP_400_BAD_REQUEST)

        deleted_count = warehouses.update(status=StatusEnum.DELETED.value)
        return Response({"deleted": deleted_count}, status=status.HTTP_204_NO_CONTENT)


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
