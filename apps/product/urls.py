from django.urls import path

from apps.product.views import ProductTestView

urlpatterns = [
    path('', ProductTestView.as_view())
]