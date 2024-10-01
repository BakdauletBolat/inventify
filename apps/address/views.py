from django.db import transaction
from drf_yasg.utils import swagger_auto_schema
from rest_framework import status
from rest_framework.generics import get_object_or_404
from rest_framework.response import Response
from rest_framework.viewsets import ModelViewSet

from apps.address import serializers
from apps.address.models import Address
from users.models.User import ClientProfile


class AddressModelViewSet(ModelViewSet):
    serializer_class = serializers.AddressSerializer
    queryset = Address.objects.all()

    @transaction.atomic
    @swagger_auto_schema(serializer_class=serializer_class,
                         responses={201: serializer_class})
    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        address = Address.objects.create(**serializer.validated_data)

        response_data = self.serializer_class(address).data
        headers = self.get_success_headers(response_data)
        return Response(response_data, status=status.HTTP_201_CREATED, headers=headers)

    def get_user_addresses(self, request, *args, **kwargs):
        user = get_object_or_404(ClientProfile, id=kwargs.get('pk'))
        addresses = Address.objects.filter(user=user)
        response_data = self.serializer_class(addresses, many=True).data
        return Response(response_data, status=status.HTTP_200_OK)
