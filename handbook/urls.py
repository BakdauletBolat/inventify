from rest_framework import routers

from handbook import views

router = routers.SimpleRouter()
router.register('city', views.CityViewSet)

urlpatterns = router.urls
