from apps.product import views
from rest_framework import routers

router = routers.SimpleRouter()
router.register('', views.ProductViewSet)

urlpatterns = router.urls
