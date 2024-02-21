from django.urls import path

from apps.car import views

urlpatterns = [
    path('modifications/', views.ProductModificationListAPIView.as_view()),
    path('manufacturers/', views.ManufacturerListAPIView.as_view()),
    path('models/', views.CarModelsListAPIView.as_view()),
    path('engines/', views.EnginesListAPIView.as_view()),
    path('filters/', views.CarFilters.as_view())
]
