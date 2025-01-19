from django.urls import path
from rest_framework_simplejwt.views import (
    TokenObtainPairView,
    TokenRefreshView,
)

from users import views
from users.otp import views as otp_views

jwt_url = [
    path('token/', TokenObtainPairView.as_view(), name='token_obtain_pair'),
    path('token/refresh/', TokenRefreshView.as_view(), name='token_refresh'),
    path('me/', views.UsersMe.as_view(), name='me'),
    path('otp/', otp_views.UserOTPView.as_view({'post': 'register'}), name='user_otp_register'),
    path('otp/token/', otp_views.UserOTPView.as_view({'post': 'verify'}), name='user_otp_verify')
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
    path('<int:pk>/orders/', views.UserViewSet.as_view({'get': 'orders'}))
]

urlpatterns = jwt_url + user_url
