import re

from rest_framework import serializers


def phone_validator(value):
    reg = re.fullmatch(r"((8|\+7|7)-?)?\(?\d{3}\)?-?\d{1}-?\d{1}-?\d{1}-?\d{1}-?\d{1}-?\d{1}-?\d{1}", value)
    if reg is None:
        raise serializers.ValidationError('Не правильный формат номера')


class UserOTPSerializer(serializers.Serializer):
    phone = serializers.CharField(max_length=15, validators=[phone_validator])


class VerifyUserSerializer(serializers.Serializer):
    otp = serializers.CharField()
    phone = serializers.CharField()
