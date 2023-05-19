from django.db import transaction
from rest_framework import viewsets, status
from rest_framework.response import Response
from apps.order import models, serializers
from django.core import exceptions


class OrderViewSet(viewsets.ModelViewSet):
    queryset = models.Order.objects.all()
    serializer_class = serializers.OrderSerializer

    @transaction.atomic
    def create(self, request, *args, **kwargs):
        try:
            return super().create(request, *args, **kwargs)
        except exceptions.ValidationError as e:
            return Response({'detail': e.message}, status=status.HTTP_422_UNPROCESSABLE_ENTITY)


