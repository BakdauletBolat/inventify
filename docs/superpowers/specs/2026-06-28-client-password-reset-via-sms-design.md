# Сброс пароля клиента по SMS-коду — дизайн

Дата: 2026-06-28
Ветка: in-8

## Цель

Клиенты входят по телефону + паролю (`POST /api/users/token/`). Email у клиентов нет (только телефон). Нужен поток «забыл пароль» для клиента **через SMS-код**, переиспользуя готовую OTP-инфраструктуру.

## Контекст

- Клиентский вход: `TokenObtainPairView` на `/api/users/token/` (телефон + пароль).
- Сотруднический вход: `/api/admin/users/token/?is_admin_user=true` (тот же view; бэкенд на параметр не реагирует — это зона отложенного разделения).
- SMS-инфраструктура уже есть:
  - `users.otp.actions.CreateUserCodeAction.run(user)` → создаёт `UserCode(otp=...)`.
  - `users.otp.actions.SmsService.send_sms(phone, sms)` → шлёт SMS (smsc.kz); кидает исключение при неудаче.
  - `users.otp.actions.GetStatusUserCodeAction.run(user, otp)` → возвращает `SmsStatus` (SUCCESS / TIMEOUT / INVALID_CODE / NOT_CREATED), окно валидности кода 5 минут.
  - `SmsStatus` — `users.otp.enums`.
- `User`: `USERNAME_FIELD='phone'` (unique). `AUTH_PASSWORD_VALIDATORS` настроены.
- Permission `InventifyAPIPermission`: пути не под `/api/admin` публичны → новые клиентские ручки доступны без авторизации.
- Существующие ручки остаются как есть: `change-password` (смена залогиненным, подходит клиенту), email-`reset-password` (для тех, у кого есть email).

## Компоненты

### 1. Сервис

В `users/services/reset_password.py` (рядом с `ResetPasswordService`) добавить логику SMS-сброса. Вынести в отдельный класс/методы, чтобы не размазывать по view:

```python
class SmsPasswordResetService:
    @staticmethod
    def send_code(user) -> None:
        otp_obj = CreateUserCodeAction.run(user)
        SmsService.send_sms(phone=user.phone, sms=otp_obj.otp)

    @staticmethod
    def confirm(user, otp: str, new_password: str) -> None:
        # set_password + save; вызывается только после успешной проверки кода во view
        user.set_password(new_password)
        user.save(update_fields=["password"])
```

Проверку кода (`GetStatusUserCodeAction`) и маппинг статусов в HTTP-ответы делаем во view (там же, где сейчас OTP-verify это делает), а не в сервисе.

### 2. Сериализаторы

В `users/serializers.py`:

```python
class PasswordResetRequestSerializer(serializers.Serializer):
    phone = serializers.CharField(required=True)

class PasswordResetConfirmSerializer(serializers.Serializer):
    phone = serializers.CharField(required=True)
    otp = serializers.CharField(required=True)
    new_password = serializers.CharField(required=True)
```

### 3. Эндпоинты

Методы на `UserViewSet` (в стиле существующих `reset_password`/`change_password`), маршруты в `users/urls.py` (клиентский путь):

**a) Запрос кода** — `POST /api/users/password-reset/request/`, тело `{ "phone": "+7..." }`:
- `user = User.objects.filter(phone=phone).first()`.
- Если найден → `SmsPasswordResetService.send_code(user)`.
- Ответ всегда `200 {"message": "Если номер зарегистрирован, на него отправлен код"}` (не раскрываем существование номера). Если SMS не отправилась (исключение `SmsService`) — ловим и всё равно отдаём `200` (не палим номер); ошибку логируем.

**b) Подтверждение** — `POST /api/users/password-reset/confirm/`, тело `{ "phone": "+7...", "otp": "1234", "new_password": "..." }`:
- `user = User.objects.filter(phone=phone).first()`; если нет → `422 {"detail": "Неправильный код, пожалуйста попробуйте еще"}` (как в OTP-verify, не раскрываем).
- `status = GetStatusUserCodeAction.run(user, otp)`:
  - `SUCCESS` → `validate_password(new_password, user)`; при ошибке → `400 {"error": [...]}`; иначе `SmsPasswordResetService.confirm(...)` → `200 {"message": "Пароль успешно изменён"}`.
  - `TIMEOUT` → `422 {"detail": "Время кода истекло"}`.
  - `INVALID_CODE` / `NOT_CREATED` → `422 {"detail": "Неправильный код, пожалуйста попробуйте еще"}`.

Маршруты:
```python
path('password-reset/request/', views.UserViewSet.as_view({'post': 'password_reset_request'})),
path('password-reset/confirm/', views.UserViewSet.as_view({'post': 'password_reset_confirm'})),
```

## Обработка ошибок

| Ситуация | Ответ |
|---|---|
| request: номер не найден | 200 (нейтрально, без утечки) |
| request: SMS не ушла | 200 (нейтрально), ошибка в лог |
| confirm: код верный, пароль валиден | 200 |
| confirm: код истёк | 422 «Время кода истекло» |
| confirm: код неверный/нет/юзер не найден | 422 «Неправильный код…» |
| confirm: новый пароль слабый | 400 с сообщениями валидатора |

## Тестирование

Тесты на уровне **сервиса** (без APIClient — иначе упрётся в импорт-тайм баг `apps/order/actions.py`). Запуск локально на throwaway SQLite, postgres не трогаем:
- `SmsPasswordResetService.confirm(user, ...)` меняет пароль (`user.check_password(new)`), старый больше не подходит.
- `send_code` создаёт `UserCode` для пользователя (мокать `SmsService.send_sms`, чтобы не слать реальную SMS).

## Вне scope

- Полноценное разделение клиент/сотрудник и реакция бэкенда на `is_admin_user` (отложено).
- Rate-limiting запроса кода.
- API-уровневые (HTTP) тесты (блокируются импорт-тайм багом order.actions).
- Изменение существующих `change-password` / email-`reset-password`.
