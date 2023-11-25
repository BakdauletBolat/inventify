from django.urls import path

from apps.category.views import CategoryListAPIView

urlpatterns = [
    path('', CategoryListAPIView.as_view())
]
