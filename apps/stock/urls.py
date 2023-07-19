from rest_framework import routers
from apps.stock import views

router = routers.SimpleRouter()
router.register('warehouses', views.WareHouseViewSet)
router.register('receipt', views.StockReceiptViewSet)

urlpatterns = router.urls
