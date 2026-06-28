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
            'get': 'list',
        })),

    path('<int:pk>/', views.UserViewSet.as_view(
        {
            'delete': 'destroy',
            'patch': 'update',
            'get': 'retrieve'
        })),
    path('bulk-delete/', views.UserViewSet.as_view({"delete": "bulk_delete"})),
    path('roles/', views.UserViewSet.as_view({'get': 'roles'})),
    path('change-password/', views.UserViewSet.as_view({'post': 'change_password'})),
    path('reset-password/', views.UserViewSet.as_view({'post': 'reset_password'})),
    path('password-reset/request/', views.UserViewSet.as_view({'post': 'password_reset_request'})),
    path('password-reset/confirm/', views.UserViewSet.as_view({'post': 'password_reset_confirm'})),
    path('orders/', views.UserViewSet.as_view({'get': 'orders'})),
    path('orders/<int:pk>/cancel/', views.UserViewSet.as_view({'post': 'cancel'}))
]

urlpatterns = jwt_url + user_url
