from django_filters.rest_framework import DjangoFilterBackend
from rest_framework.generics import ListAPIView
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework.mixins import RetrieveModelMixin, ListModelMixin
from rest_framework.viewsets import GenericViewSet

from apps.car.filters import *
from apps.car.serializers import *
from apps.car.services.get_filters import GetFilters


# Create your views here.
class ProductModificationListAPIView(ListAPIView):
    queryset = Modification.objects.all()
    serializer_class = ModificationSerializer
    filter_backends = [DjangoFilterBackend]
    filterset_class = ModificationFilter


class ManufacturerListAPIView(GenericViewSet, ListModelMixin, RetrieveModelMixin):
    queryset = ManufacturerType.objects.all()
    serializer_class = ManufacturerTypeSerializer
    filter_backends = [DjangoFilterBackend]
    filterset_class = ManufacturerFilter


class CarModelsListAPIView(ListAPIView):
    queryset = ModelCar.objects.all()
    serializer_class = ModelCarSerializer
    filter_backends = [DjangoFilterBackend]
    filterset_class = ModelCarFilter


class EnginesListAPIView(ListAPIView):
    queryset = Engine.objects.all()
    serializer_class = EngineSerializer
    filter_backends = [DjangoFilterBackend]
    filterset_class = EngineFilter


class CarFilters(APIView):
    def get(self, request, *args, **kwargs):
        return Response(data=GetFilters().run(), status=200)
