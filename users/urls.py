from django.urls import path
from rest_framework_simplejwt.views import (
    TokenObtainPairView,
    TokenRefreshView,
)

from users.views import (UserListCreateView,
                         UserRetrieveUpdateDestroyAPIView)

jwt_url = [
    path('token/', TokenObtainPairView.as_view(), name='token_obtain_pair'),
    path('token/refresh/', TokenRefreshView.as_view(), name='token_refresh')
]

user_url = [
    path('', UserListCreateView.as_view(), name='user_list_create'),
    path('<int:pk>/', UserRetrieveUpdateDestroyAPIView.as_view(), name='user_retrieve_update_destroy'),
]

urlpatterns = jwt_url + user_url
