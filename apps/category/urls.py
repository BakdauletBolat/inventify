from django.urls import path

from apps.category import views

urlpatterns = [
    path('', views.CategoryListAPIView.as_view({'get': 'list'})),
    path('<int:pk>/', views.CategoryListAPIView.as_view({'get': 'retrieve'})),
    path('tree/', views.CategoryTreeAPIView.as_view())
]
