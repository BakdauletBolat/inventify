import os

import requests

from users.otp.enums import SmsStatus


class SmsRequest:

    @staticmethod
    def send_sms(phone: str, msg):
        phone = phone.split('+')[1]
        mes = f"Ваш код: {msg}"
        response = requests.post(url="https://smsc.kz/sys/send.php",
                                params={
                                    "login": os.environ.get('sms_login'),
                                    "psw": os.environ.get('sms_psw'),
                                    "phones": phone,
                                    "mes": mes
                                })
        status = response.content.decode('utf-8').split(' ')[0]
        data = {
            "status": SmsStatus.SUCCESS if status == 'OK' else SmsStatus.NOT_CREATED,
        }
        return data
