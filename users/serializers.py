from django.contrib.auth.hashers import make_password
from django.contrib.auth.password_validation import validate_password
from rest_framework import serializers

from handbook.models import City
from users.models.Address import Address
from users.models.User import User


class UserSerializer(serializers.ModelSerializer):
    city = serializers.PrimaryKeyRelatedField(queryset=City.objects.all())

    class Meta:
        model = User
        extra_kwargs = {
            "profile_type": {"required": True},
            "password": {"write_only": True, 'required': False}
        }
        fields = ('__all__')
        # exclude = ('user_permissions', )


class UserRegisterSerializer(UserSerializer):
    password = serializers.CharField(write_only=True, required=True, validators=[validate_password])
    password2 = serializers.CharField(write_only=True, required=True)

    def validate(self, attrs):
        if attrs['password'] != attrs['password2']:
            raise serializers.ValidationError({"password": "Password fields didn't match."})
        attrs['password'] = make_password(attrs['password'])
        attrs.pop('password2')
        return attrs


class AddressSerializer(serializers.ModelSerializer):
    user = UserSerializer()
    street = serializers.CharField(write_only=True, required=True)

    class Meta:
        model = Address
        exclude = ('city',)
