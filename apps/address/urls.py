from django.urls import path, include
from rest_framework import routers

from apps.address import views

router = routers.SimpleRouter()
router.register('', views.AddressModelViewSet)

urlpatterns = [
    path('', include(router.urls)),
    path('user/<int:pk>/', views.AddressModelViewSet.as_view({'get': 'get_user_addresses'}))
]
