from django.urls import path
from rest_framework import routers

from apps.stock import views
from apps.stock.views import MoveProductViewSet

router = routers.SimpleRouter()
router.register('warehouses', views.WareHouseViewSet)

urlpatterns = router.urls

urlpatterns += [
    path('move/', MoveProductViewSet.as_view({'post': 'move'}))
]
