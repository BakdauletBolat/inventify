from django.contrib.auth.hashers import make_password
from django.contrib.auth.password_validation import validate_password
from rest_framework import serializers
from rest_framework.exceptions import PermissionDenied

from base.enums import StatusEnum
from handbook.models import City
from handbook.serializers import CitySerializer
from users.enums import RoleEnum
from users.models.User import User, Role


class RoleSerializer(serializers.ModelSerializer):
    class Meta:
        model = Role
        fields = '__all__'


class UserSerializer(serializers.ModelSerializer):
    city = CitySerializer(read_only=True)
    roles = RoleSerializer(many=True, read_only=True)

    class Meta:
        model = User
        extra_kwargs = {
            "password": {"write_only": True, 'required': False}
        }
        fields = ('__all__')
        # exclude = ('user_permissions', )


class UserUpdateSerializer(UserSerializer):
    roles = serializers.ListSerializer(required=False,
                                       child=serializers.PrimaryKeyRelatedField(queryset=Role.objects.all())
                                       )
    city = serializers.PrimaryKeyRelatedField(queryset=City.objects.all(), required=False)
    status = serializers.ChoiceField(choices=StatusEnum.choices)

    class Meta(UserSerializer.Meta):
        extra_kwargs = {
            "first_name": {'required': False},
            "phone": {'required': False},
            "last_name": {'required': False},
            "password": {'required': False},
        }

    def update(self, instance, validated_data):
        # Обновляем роли
        roles_data = validated_data.pop('roles', None)
        if roles_data is not None:
            instance.roles.set(roles_data)  # Устанавливаем новые роли

        # Обновляем остальные поля
        for attr, value in validated_data.items():
            setattr(instance, attr, value)

        # Сохраняем изменения
        instance.save()
        return instance

    def validate(self, attrs):
        request = self.context['request']
        user = request.user

        is_director = user.is_superuser or user.roles.filter(name=RoleEnum.DIRECTOR.value).exists()

        # Менять роли и признак сотрудника (is_staff) может только директор/суперпользователь
        if ('roles' in attrs or 'is_staff' in attrs) and not is_director:
            raise PermissionDenied("Менять роли и признак сотрудника может только директор.")

        # is_superuser=True — только суперпользователь
        if attrs.get('is_superuser') and not user.is_superuser:
            raise PermissionDenied("Только суперпользователь может назначить is_superuser=True.")

        return super().validate(attrs)


class UserRegisterSerializer(UserSerializer):
    password = serializers.CharField(write_only=True, required=True, validators=[validate_password])
    password2 = serializers.CharField(write_only=True, required=True)
    roles = serializers.ListSerializer(required=False,
                                       child=serializers.PrimaryKeyRelatedField(queryset=Role.objects.all()),
                                       allow_empty=True)
    city = serializers.PrimaryKeyRelatedField(queryset=City.objects.all(), required=True)

    def validate(self, attrs):
        request = self.context.get('request')
        user = getattr(request, 'user', None)
        is_director = bool(
            user and (user.is_superuser or user.roles.filter(name=RoleEnum.DIRECTOR.value).exists())
        )
        if (attrs.get('roles') or attrs.get('is_staff')) and not is_director:
            raise PermissionDenied("Создавать сотрудников и назначать роли может только директор.")
        if attrs.get('is_superuser') and not (user and user.is_superuser):
            raise PermissionDenied("Только суперпользователь может назначить is_superuser=True.")

        if attrs['password'] != attrs['password2']:
            raise serializers.ValidationError({"password": "Password fields didn't match."})
        attrs['password'] = make_password(attrs['password'])
        attrs.pop('password2')
        return attrs


class ChangePasswordSerializer(serializers.Serializer):
    old_password = serializers.CharField(required=True)
    new_password = serializers.CharField(required=True)


class ResetPasswordRequestSerializer(serializers.Serializer):
    phone = serializers.CharField(required=True)


class PasswordResetRequestSerializer(serializers.Serializer):
    phone = serializers.CharField(required=True)


class PasswordResetConfirmSerializer(serializers.Serializer):
    phone = serializers.CharField(required=True)
    otp = serializers.CharField(required=True)
    new_password = serializers.CharField(required=True)