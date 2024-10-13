from django.urls import path
from rest_framework import routers

from apps.car import views

router = routers.SimpleRouter()
router.register('color', views.ColorModelViewSet)
router.register('quality', views.QualityModelViewSet)


urlpatterns = [
    path('modifications/', views.ProductModificationListAPIView.as_view()),
    path('manufacturers/', views.ManufacturerListAPIView.as_view({'get': 'list'})),
    path('<int:pk>/manufacturers/', views.ManufacturerListAPIView.as_view({'get': 'retrieve'})),
    path('models/', views.CarModelsListAPIView.as_view()),
    path('engines/', views.EnginesListAPIView.as_view()),
    path('filters/', views.CarFilters.as_view())
] + router.urls
