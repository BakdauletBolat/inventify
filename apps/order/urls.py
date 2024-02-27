from django.urls import path
from rest_framework import routers

from apps.order import views

router = routers.SimpleRouter()
router.register('', views.OrderViewSet)

urlpatterns = router.urls

urlpatterns += [
    path('<int:pk>/confirm/', views.OrderConfirmView.as_view())
]
