# Сброс и смена пароля пользователя — дизайн

Дата: 2026-06-27
Ветка: in-8

## Цель

Три механизма работы с паролем:

1. **Admin action** — персонал сбрасывает пароль пользователя на фиксированный `Zz123456` через action в Django-админке. **Без письма.**
2. **API-сброс («забыл пароль»)** — публичный эндпоинт: по телефону находим пользователя, генерируем **случайный** пароль и **шлём его на email**.
3. **API смены пароля** — авторизованный пользователь сам меняет пароль (`old_password` → `new_password`).

## Контекст

- Email-инфраструктуры в проекте нет (нет `EMAIL_BACKEND`, SMTP-настроек, `send_mail`). Есть только SMS (smsc.kz) для OTP.
- `User` (`users/models/User.py`): `USERNAME_FIELD = 'phone'` (unique), поле `email` nullable и НЕ unique.
- Эндпоинт `UserViewSet.change_password` и маршрут `change-password/` уже частично присутствуют в незакоммиченных изменениях рабочего дерева.
- `AUTH_PASSWORD_VALIDATORS` уже настроены в `inventify/settings/base.py`.
- Permission `InventifyAPIPermission`: пути под `/api/admin` требуют staff, остальные `/api/...` — публичны. Значит `/api/users/reset-password/` доступен без авторизации.
- Паттерны: бизнес-логика в сервисах/actions (см. `users/otp/actions.py`), маршруты `UserViewSet` мапятся вручную в `users/urls.py`.

## Компоненты

### 1. SMTP-конфигурация

В `inventify/settings/base.py` добавить env-driven блок:

```python
EMAIL_BACKEND = os.environ.get('EMAIL_BACKEND', 'django.core.mail.backends.console.EmailBackend')
EMAIL_HOST = os.environ.get('EMAIL_HOST', 'smtp.gmail.com')
EMAIL_PORT = int(os.environ.get('EMAIL_PORT', 587))
EMAIL_USE_TLS = int(os.environ.get('EMAIL_USE_TLS', 1))
EMAIL_HOST_USER = os.environ.get('EMAIL_HOST_USER', '')
EMAIL_HOST_PASSWORD = os.environ.get('EMAIL_HOST_PASSWORD', '')
DEFAULT_FROM_EMAIL = os.environ.get('DEFAULT_FROM_EMAIL', EMAIL_HOST_USER)
```

Дефолт backend — `console` (печать в консоль), чтобы без кредов ничего не падало в dev. Плейсхолдеры добавить в `.env.example`. Прод подключит реальный бесплатный SMTP (Gmail app-password / Yandex / Mail.ru) через `.env`.

### 2. Сервис сброса пароля

Новый файл `users/services/reset_password.py`:

```python
from django.conf import settings
from django.core.mail import send_mail
from django.utils.crypto import get_random_string

DEFAULT_PASSWORD = "Zz123456"

class ResetPasswordService:
    @staticmethod
    def reset_to_default(user) -> None:
        """Admin action: фиксированный пароль, без письма."""
        user.set_password(DEFAULT_PASSWORD)
        user.save(update_fields=["password"])

    @staticmethod
    def reset_random_and_email(user) -> None:
        """API: случайный пароль + письмо на email пользователя."""
        new_password = get_random_string(10)
        user.set_password(new_password)
        user.save(update_fields=["password"])
        send_mail(
            subject="Сброс пароля — Kaynaravto",
            message=f"Ваш новый пароль: {new_password}\nСмените его после входа.",
            from_email=settings.DEFAULT_FROM_EMAIL,
            recipient_list=[user.email],
            fail_silently=False,
        )
```

### 3. Admin action

В `users/admin.py`, в `UserAdmin`:

```python
actions = ['reset_password']

@admin.action(description="Сбросить пароль на Zz123456")
def reset_password(self, request, queryset):
    for user in queryset:
        ResetPasswordService.reset_to_default(user)
    self.message_user(request, f"Пароль сброшен у {queryset.count()} пользователей.")
```

Работает для одного и нескольких выбранных. Email НЕ отправляется. Добавить `email` в `list_display`.

### 4. API-сброс пароля («забыл пароль»)

- Сериализатор `ResetPasswordRequestSerializer` (`users/serializers.py`): поле `phone` (required).
- Метод `UserViewSet.reset_password(request)`:
  - Валидирует `phone`.
  - `user = User.objects.filter(phone=...).first()`; если нет → 404 `{"error": "Пользователь не найден"}`.
  - Если у пользователя нет `email` → 400 `{"error": "У пользователя не указан email"}`.
  - Иначе `ResetPasswordService.reset_random_and_email(user)` → 200 `{"message": "Новый пароль отправлен на email"}`.
- Маршрут в `users/urls.py`: `POST /api/users/reset-password/`. Публичный (permission уже допускает не-`/api/admin` пути).

### 5. API смены пароля

Доработать существующий `UserViewSet.change_password` (`users/views.py`):
- `old_password`, `new_password` (поле `new_password2` НЕ добавляется).
- `user.check_password(old_password)` → 400 при несовпадении.
- Валидация нового пароля через `django.contrib.auth.password_validation.validate_password` (использует `AUTH_PASSWORD_VALIDATORS`); ошибки → 400.
- `user.set_password(new_password)` + `save()` → 200.
- Маршрут `POST /api/users/change-password/`, требует авторизованного `request.user`.

`ChangePasswordSerializer` уже есть в `users/serializers.py`.

## Обработка ошибок

| Ситуация | Ответ |
|---|---|
| API-сброс: пользователь по phone не найден | 404 `{"error": "Пользователь не найден"}` |
| API-сброс: у пользователя нет email | 400 `{"error": "У пользователя не указан email"}` |
| API-сброс: SMTP недоступен | `fail_silently=False` → 500/исключение (пароль уже изменён) |
| Смена: неверный старый пароль | 400 `{"error": "Неправильный пароль"}` |
| Смена: новый пароль не прошёл валидацию | 400 с сообщениями валидатора |

## Тестирование

- Сервис `reset_to_default` → `user.check_password("Zz123456")`.
- Сервис `reset_random_and_email` → пароль изменён, письмо в `mail.outbox` (locmem backend в тестах), содержит новый пароль.
- Admin action → пароль `Zz123456` у всех выбранных пользователей.
- API-сброс: валидный phone с email → 200 + письмо; phone без email → 400; несуществующий phone → 404.
- API-смена: верный старый + валидный новый → 200; неверный старый → 400; слабый новый → 400.

## Вне scope

- Сброс по одноразовой ссылке/токену (шлём сам пароль, не ссылку).
- Подтверждение нового пароля (`new_password2`).
- Идентификация при сбросе по email (только по phone).
- Rate-limiting публичного эндпоинта сброса.
