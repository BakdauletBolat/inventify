from django.urls import path, include

from apps.product import views

urlpatterns = [
    path('product/', include([
        path('image/', views.ProductImageView.as_view(), name='create_image'),
        path('image/<int:pk>/', views.ProductImageView.as_view(), name='delete_image')
    ])),
    path('v2/product/', include([
        path('', views.ProductViewSetV2.as_view({'get': 'list'})),
        path('create/', views.ProductViewSetV2.as_view({'post': 'create'})),
        path('<int:pk>/', views.ProductViewSetV2.as_view({'get': 'retrieve'})),
        path('<int:pk>/delete/', views.ProductViewSetV2.as_view({'delete': 'destroy'})),
        path('<int:pk>/update/', views.ProductViewSetV2.as_view({'patch': 'update'})),
        path('assign-warehouse/', views.ProductViewSetV2.as_view({'post': 'assign_warehouse'}))

    ]))
]
