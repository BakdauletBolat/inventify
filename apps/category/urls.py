from django.urls import path

from apps.category import views

urlpatterns = [
    path('', views.CategoryListAPIView.as_view()),
    path('tree/', views.CategoryTreeAPIView.as_view())
]
