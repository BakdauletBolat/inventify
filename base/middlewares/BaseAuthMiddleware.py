import jwt
from django.conf import settings
from users.models.User import User
from rest_framework.authentication import BaseAuthentication
from rest_framework.exceptions import AuthenticationFailed


class CustomJWTAuthentication(BaseAuthentication):
    def authenticate(self, request):
        auth_header = request.headers.get('Authorization')
        if not auth_header:
            return None

        parts = auth_header.split()
        if len(parts) != 2 or parts[0].lower() != 'bearer':
            raise AuthenticationFailed('Неверный формат токена.')

        token = parts[1]

        try:
            payload = jwt.decode(token, settings.SECRET_KEY, algorithms=['HS256'])
        except jwt.ExpiredSignatureError:
            raise AuthenticationFailed('Токен истек.')
        except jwt.InvalidTokenError:
            raise AuthenticationFailed('Неверный токен.')

        user_id = payload.get('user_id')
        if not user_id:
            raise AuthenticationFailed('Отсутствует идентификатор пользователя в токене.')

        try:
            user = User.objects.get(id=user_id)
        except User.DoesNotExist:
            raise AuthenticationFailed('Пользователь не найден.')

        return (user, None)
