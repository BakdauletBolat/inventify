import random

from django.db import transaction
from rest_framework import viewsets, status
from rest_framework.generics import get_object_or_404
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework_simplejwt.tokens import RefreshToken

from users.models.User import User
from users.otp.actions import CreateUserCodeAction, SmsService, GetStatusUserCodeAction
from users.otp.enums import SmsStatus
from users.otp.serializers import UserOTPSerializer, VerifyUserSerializer
from users.serializers import UserSerializer


def get_tokens_for_user(user, request):
    refresh = RefreshToken.for_user(user)
    return {
        'user': UserSerializer(user, context={'request': request}).data,
        'refresh': str(refresh),
        'access': str(refresh.access_token),
    }


class UserOTPView(viewsets.ViewSet, APIView):

    def register(self, request, *args, **kwargs):
        serializer = UserOTPSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        with transaction.atomic():
            user, created = User.objects.get_or_create(phone=serializer.validated_data['phone'])
            try:
                if created:
                    user.set_password(f"{random.randint(100000, 999999)}")
                    user.save()
                    user.roles.add(1535)
                otp_obj = CreateUserCodeAction().run(user=user)
                if not request.data.get('test', False):
                    SmsService.send_sms(phone=user.phone, sms=otp_obj.otp)
                return Response({'status': 'success'}, status=200)
            except Exception as e:
                return Response({'status': str(e)}, status=400)

    def verify(self, request, *args, **kwargs):
        with transaction.atomic():
            serializer = VerifyUserSerializer(data=request.data)

            if serializer.is_valid(raise_exception=True):
                phone_number = serializer.validated_data['phone']
                otp = serializer.validated_data['otp']
                user = get_object_or_404(User, phone=phone_number)

                code_status = GetStatusUserCodeAction.run(user=user,
                                                          otp=otp)

                if code_status == SmsStatus.SUCCESS:
                    data = get_tokens_for_user(user, request)
                    return Response(data)
                elif code_status == SmsStatus.TIMEOUT:
                    return Response({'details': 'Время кода истекло'}, status=status.HTTP_422_UNPROCESSABLE_ENTITY)
                elif code_status == SmsStatus.INVALID_CODE:
                    return Response({'details': 'Не правильный код, пожалуйста попробуйте еще'},
                                    status=status.HTTP_422_UNPROCESSABLE_ENTITY)
                else:
                    return Response({'details': 'Не правильный код, пожалуйста попробуйте еще'},
                                    status=status.HTTP_422_UNPROCESSABLE_ENTITY)
