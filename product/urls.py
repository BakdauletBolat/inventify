from django.urls import path

from product.views import ProductTestView

urlpatterns = [
    path('', ProductTestView.as_view())
]