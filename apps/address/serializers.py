from rest_framework import serializers

from handbook.models import City
from handbook.serializers import CitySerializer
from apps.address.models import Address
from users.models.User import ClientProfile
from users.serializers import UserSerializer


class AddressSerializer(serializers.ModelSerializer):
    user_id = serializers.PrimaryKeyRelatedField(queryset=ClientProfile.objects.all(), allow_null=True, required=False,
                                                 source='user', write_only=True)
    user = UserSerializer(read_only=True)
    city_id = serializers.PrimaryKeyRelatedField(queryset=City.objects.all(), allow_null=True, required=False,
                                                 source='city', write_only=True)
    city = CitySerializer(read_only=True)

    class Meta:
        model = Address
        fields = '__all__'
