from rest_framework import generics
from rest_framework import permissions
from rest_framework import status
from rest_framework.response import Response
from rest_framework.views import APIView

from users.actions import CreateUserAction
from users.models.User import User
from users import serializers


class UserListCreateView(generics.ListCreateAPIView):
    queryset = User.objects.all()
    serializer_class = serializers.UserSerializer

    def create(self, request, *args, **kwargs):
        serializer = serializers.UserRegisterSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        user = CreateUserAction(data=serializer.validated_data).run()
        response_data = self.serializer_class(user).data
        headers = self.get_success_headers(response_data)
        return Response(response_data, status=status.HTTP_201_CREATED, headers=headers)


class UserRetrieveUpdateDestroyAPIView(generics.RetrieveUpdateDestroyAPIView):
    queryset = User.objects.all()
    serializer_class = serializers.UserSerializer


class UsersMe(APIView):
    permission_classes = (permissions.IsAuthenticated,)

    @staticmethod
    def get(request, *args, **kwargs):
        user = request.user
        serializer = serializers.UserSerializer(user)
        return Response(serializer.data, status=status.HTTP_200_OK)
