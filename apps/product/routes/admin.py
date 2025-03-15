from django.urls import path, include

from apps.product import views

## Для админки

urlpatterns = [
    path('image/', views.AdminProductImageView.as_view(), name='create_image'),
    path('image/<int:pk>/', views.AdminProductImageView.as_view(), name='delete_image'),
    path('v2/product/', include([
        path('', views.AdminProductViewSetV2.as_view({'get': 'list'})),
        path('bulk-delete/', views.AdminProductViewSetV2.as_view({'delete': 'bulk_delete'})),
        path('create/', views.AdminProductViewSetV2.as_view({'post': 'create'})),
        path('<int:pk>/', views.AdminProductViewSetV2.as_view({'get': 'retrieve'})),
        path('<int:pk>/delete/', views.AdminProductViewSetV2.as_view({'delete': 'destroy'})),
        path('<int:pk>/update/', views.AdminProductViewSetV2.as_view({'patch': 'update'})),
        path('assign-warehouse/', views.AdminProductViewSetV2.as_view({'post': 'assign_warehouse'}))
    ]))
]