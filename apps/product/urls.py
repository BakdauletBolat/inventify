from django.urls import path

from apps.product import views

urlpatterns = [
    path('', views.ProductViewSet.as_view(), name='create_list_product'),
    path('<int:pk>/', views.ProductViewSet.as_view(), name='get_update_destroy_product'),
    path('image/', views.ProductImageView.as_view(), name='create_image'),
    path('image/<int:pk>/', views.ProductImageView.as_view(), name='delete_image')
]
