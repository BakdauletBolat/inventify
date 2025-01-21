import os

import requests


class TelegramRequest:
    telegram_api = os.environ.get('TELEGRAM_URL')

    def send_sms_feedback(self, message):
        telegram_token_404 = os.environ.get('TELEGRAM_FEEDBACK_BOT_TOKEN', None)
        telegram_url_404 = self.telegram_api + telegram_token_404 + '/sendMessage'
        telegram_chat_id = os.environ.get('TELEGRAM_FEEDBACK_CHAT_ID')

        response = requests.get(url=f'{telegram_url_404}?chat_id={telegram_chat_id}&text={message}')
        return response