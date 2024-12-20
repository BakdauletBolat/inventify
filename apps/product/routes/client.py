from django.urls import path, include

from apps.product import views

## Для админки

urlpatterns = [
    path('', include([
        path('', views.ProductViewSet.as_view({'get': 'list'})),
        path('<int:pk>/', views.ProductViewSet.as_view({'get': 'retrieve'})),
    ]))
]