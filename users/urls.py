from django.urls import path, include
from rest_framework import routers
from rest_framework_simplejwt.views import (
    TokenObtainPairView,
    TokenRefreshView,
)

from users import views

router = routers.SimpleRouter()
router.register('', views.AddressModelViewSet)

jwt_url = [
    path('token/', TokenObtainPairView.as_view(), name='token_obtain_pair'),
    path('token/refresh/', TokenRefreshView.as_view(), name='token_refresh'),
    path('me/', views.UsersMe.as_view(), name='me')
]

user_url = [
    path('', views.UserListCreateView.as_view(), name='user_list_create'),
    path('<int:pk>/', views.UserRetrieveUpdateDestroyAPIView.as_view(), name='user_retrieve_update_destroy'),
    path('address/', include(router.urls))
]

urlpatterns = jwt_url + user_url
