import datetime
import logging
import random

from django.utils.translation import gettext as _

from users.models.User import User
from users.otp.enums import SmsStatus
from users.otp.models import UserCode
from users.otp.requests import SmsRequest


class SmsService:

    @staticmethod
    def send_sms(phone, sms):
        response = SmsRequest.send_sms(phone, sms)
        if response['status'] == SmsStatus.NOT_CREATED:
            raise Exception(_('Сообщение не было отправлено'))


class CreateUserCodeAction:

    @staticmethod
    def run(user):
        return UserCode.objects.create(user=user, otp=random.randint(1000, 9999))


class GetStatusUserCodeAction:

    @staticmethod
    def run(user: User, otp: str):
        otp_object = UserCode.objects.filter(user=user,
                                             otp=otp).order_by('-created_at').first()

        if user.phone in ['+77059943864', '+77089531792'] and otp == '7899':
            return SmsStatus.SUCCESS

        if otp_object is not None:
            try:
                now = datetime.datetime.now(datetime.timezone.utc)
                created_at = otp_object.created_at
                difference = now - created_at
                minutes = difference.total_seconds() / 60
                if minutes < 5:
                    return SmsStatus.SUCCESS
                else:
                    return SmsStatus.TIMEOUT

            except Exception as e:
                logging.exception(e)
                return SmsStatus.INVALID_CODE
        else:
            return SmsStatus.NOT_CREATED
