from rest_framework import permissions
from rest_framework import status
from rest_framework import viewsets
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView

from inventify.permissions import IsManager, IsDirector
from users import serializers
from users.actions import CreateUserAction
from users.models.User import User, Role


class UserViewSet(viewsets.ModelViewSet):
    queryset = User.objects.all().order_by('id')
    serializer_class = serializers.UserSerializer
    permission_classes = [IsAuthenticated, IsManager]

    def get_permissions(self):
        """
        Добавляем кастомные разрешения для действий, таких как удаление.
        """
        if self.request.method == 'DELETE':
            return [IsDirector()]
        return super().get_permissions()

    def update(self, request, *args, **kwargs):
        partial = kwargs.pop('partial', False)
        instance = self.get_object()
        serializer = serializers.UserUpdateSerializer(instance, data=request.data, partial=partial,
                                                      context={'request': request})
        serializer.is_valid(raise_exception=True)
        self.perform_update(serializer)
        if getattr(instance, '_prefetched_objects_cache', None):
            instance._prefetched_objects_cache = {}
        response_data = self.serializer_class(self.get_object()).data
        return Response(response_data)

    def create(self, request, *args, **kwargs):
        serializer = serializers.UserRegisterSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        user = CreateUserAction(data=serializer.validated_data).run()
        response_data = self.serializer_class(user).data
        headers = self.get_success_headers(response_data)
        return Response(response_data, status=status.HTTP_201_CREATED, headers=headers)

    def roles(self, request, *args, **kwargs):
        return Response(Role.objects.all().values('id', 'name'), status=status.HTTP_200_OK)


class UsersMe(APIView):
    permission_classes = (permissions.IsAuthenticated,)

    @staticmethod
    def get(request, *args, **kwargs):
        user = request.user
        serializer = serializers.UserSerializer(user)
        return Response(serializer.data, status=status.HTTP_200_OK)
