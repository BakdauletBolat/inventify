from django_filters.rest_framework import DjangoFilterBackend
from rest_framework import permissions
from rest_framework import status
from rest_framework import viewsets
from rest_framework.generics import get_object_or_404
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView

from apps.order.actions import OrderAction
from apps.order.models import Order
from apps.order.serializers import OrderSerializer
from base.enums import StatusEnum
from inventify.permissions import IsDirector
from users import serializers
from users.actions import CreateUserAction
from users.filters import UserFilter
from users.models.User import User, Role


class UserViewSet(viewsets.ModelViewSet):
    queryset = User.objects.all().order_by('id')
    serializer_class = serializers.UserSerializer
    filter_backends = [DjangoFilterBackend]
    filterset_class = UserFilter

    def get_permissions(self):
        """
        Добавляем кастомные разрешения для действий, таких как удаление.
        """
        if self.request.method == 'DELETE':
            return [IsDirector()]
        if self.action == 'orders':
            return [IsAuthenticated()]
        return super().get_permissions()

    def update(self, request, *args, **kwargs):
        partial = kwargs.pop('partial', False)
        instance = request.user
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

    def orders(self, request, *args, **kwargs):
        self.check_permissions(request)

        instance = request.user
        orders = Order.objects.filter(user=instance).order_by('-created_at')
        page = self.paginate_queryset(orders)
        if page is not None:
            serializer = OrderSerializer(page, many=True, context={"request": request})
            return self.get_paginated_response(serializer.data)

        serializer = OrderSerializer(orders, many=True)
        return Response(serializer.data)

    def cancel(self, request, *args, **kwargs):
        self.check_permissions(request)
        instance = request.user
        order = get_object_or_404(Order, user=instance, id=self.kwargs.get('pk'))
        OrderAction().delete(order)
        return Response(status=status.HTTP_204_NO_CONTENT)

    def bulk_delete(self, request):
        """ Массовое удаление пользователей """
        self.check_permissions(request)

        user_ids = request.data.get("ids", [])
        users = User.objects.filter(id__in=user_ids, status=StatusEnum.ACTIVE.value)
        if users.exists() is False:
            return Response({"error": "Не переданы ID пользователей или они были удалены"}, status=status.HTTP_400_BAD_REQUEST)

        deleted_count = users.update(status=StatusEnum.DELETED.value)
        return Response({"deleted": deleted_count}, status=status.HTTP_204_NO_CONTENT)


class UsersMe(APIView):
    permission_classes = (permissions.IsAuthenticated,)

    @staticmethod
    def get(request, *args, **kwargs):
        user = request.user
        serializer = serializers.UserSerializer(user)
        return Response(serializer.data, status=status.HTTP_200_OK)
