from django.urls import path
from rest_framework_simplejwt.views import (
    TokenObtainPairView,
    TokenRefreshView,
)

from users import views

jwt_url = [
    path('token/', TokenObtainPairView.as_view(), name='token_obtain_pair'),
    path('token/refresh/', TokenRefreshView.as_view(), name='token_refresh'),
    path('me/', views.UsersMe.as_view(), name='me')
]

user_url = [

    path('', views.UserViewSet.as_view(
        {
            'post': 'create',
            'get': 'list'
        })),

    path('<int:pk>/', views.UserViewSet.as_view(
        {
            'delete': 'destroy',
            'patch': 'update',
            'get': 'retrieve'
        })),

    path('roles/', views.UserViewSet.as_view({'get': 'roles'})),
]

urlpatterns = jwt_url + user_url
