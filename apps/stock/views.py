from django.shortcuts import render
from rest_framework import permissions, viewsets
from apps.stock import models, serializers


class WareHouseViewSet(viewsets.ModelViewSet):
    # permission_classes = (permissions.IsAuthenticated, )
    queryset = models.Warehouse.objects.all()
    serializer_class = serializers.WareHouseSerializer


class StockReceiptViewSet(viewsets.ModelViewSet):
    queryset = models.StockReceipt.objects.all()
    serializer_class = serializers.StockReceiptSerializer
