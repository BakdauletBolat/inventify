# Password Reset and Change Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Add three password operations — an admin action to reset a user's password to `Zz123456`, a public API to reset a forgotten password (random password emailed), and an authenticated API to change one's own password.

**Architecture:** Business logic lives in a new `ResetPasswordService` (`users/services/`). The admin action calls the no-email reset; a public DRF endpoint on `UserViewSet` calls the random-password-and-email reset; the existing `change_password` endpoint is hardened with Django's password validators. Email is configured via env-driven SMTP settings (console backend by default).

**Tech Stack:** Django 4.1, Django REST Framework, Django admin, Django `send_mail`, `django.contrib.auth.password_validation`.

## Global Constraints

- All run/test commands execute inside Docker: `docker-compose exec web poetry run python manage.py <cmd>`.
- Domain text (messages, `verbose_name`, `description`) is in **Russian**.
- `User.USERNAME_FIELD = 'phone'` (unique); `email` is nullable and NOT unique.
- Default password is the literal string `Zz123456` (admin reset only).
- Create test users with a valid KZ phone format: `+77770000001` etc. (regex `^\+7...`), via `User.objects.create_user(phone, password, email=...)`.
- DRF permission `InventifyAPIPermission` already makes any non-`/api/admin` path public, so `/api/users/reset-password/` needs no extra permission config.
- Commit ONLY the files listed in each task (the branch has unrelated uncommitted work — never `git add -A`).

---

### Task 1: SMTP email configuration

**Files:**
- Modify: `inventify/settings/base.py` (append email block after the `CACHES`/EAV block, near line 206)
- Modify: `.env.example`

**Interfaces:**
- Produces: settings `DEFAULT_FROM_EMAIL`, `EMAIL_BACKEND`, `EMAIL_HOST`, `EMAIL_PORT`, `EMAIL_USE_TLS`, `EMAIL_HOST_USER`, `EMAIL_HOST_PASSWORD` — consumed by Task 2's `send_mail`.

- [ ] **Step 1: Add the email settings block**

In `inventify/settings/base.py`, append:

```python
# Email
EMAIL_BACKEND = os.environ.get('EMAIL_BACKEND', 'django.core.mail.backends.console.EmailBackend')
EMAIL_HOST = os.environ.get('EMAIL_HOST', 'smtp.gmail.com')
EMAIL_PORT = int(os.environ.get('EMAIL_PORT', 587))
EMAIL_USE_TLS = int(os.environ.get('EMAIL_USE_TLS', 1))
EMAIL_HOST_USER = os.environ.get('EMAIL_HOST_USER', '')
EMAIL_HOST_PASSWORD = os.environ.get('EMAIL_HOST_PASSWORD', '')
DEFAULT_FROM_EMAIL = os.environ.get('DEFAULT_FROM_EMAIL', EMAIL_HOST_USER)
```

- [ ] **Step 2: Add placeholders to `.env.example`**

Append:

```
EMAIL_BACKEND=django.core.mail.backends.console.EmailBackend
EMAIL_HOST=smtp.gmail.com
EMAIL_PORT=587
EMAIL_USE_TLS=1
EMAIL_HOST_USER=
EMAIL_HOST_PASSWORD=
DEFAULT_FROM_EMAIL=
```

- [ ] **Step 3: Verify Django loads settings without error**

Run: `docker-compose exec web poetry run python manage.py check`
Expected: `System check identified no issues`.

- [ ] **Step 4: Commit**

```bash
git add inventify/settings/base.py .env.example
git commit -m "feat(users): add env-driven SMTP email configuration"
```

---

### Task 2: ResetPasswordService

**Files:**
- Create: `users/services/__init__.py` (empty)
- Create: `users/services/reset_password.py`
- Test: `users/tests.py`

**Interfaces:**
- Consumes: email settings from Task 1.
- Produces:
  - `users.services.reset_password.DEFAULT_PASSWORD` = `"Zz123456"`
  - `ResetPasswordService.reset_to_default(user) -> None` — sets password to `DEFAULT_PASSWORD`, no email.
  - `ResetPasswordService.reset_random_and_email(user) -> None` — sets a random password, emails it to `user.email`.

- [ ] **Step 1: Write the failing tests**

Replace `users/tests.py` contents with:

```python
from django.core import mail
from django.test import TestCase

from users.models.User import User
from users.services.reset_password import DEFAULT_PASSWORD, ResetPasswordService


class ResetPasswordServiceTest(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(
            phone="+77770000001", password="oldpass123", email="u1@example.com"
        )

    def test_reset_to_default_sets_fixed_password_and_sends_no_email(self):
        ResetPasswordService.reset_to_default(self.user)
        self.user.refresh_from_db()
        self.assertTrue(self.user.check_password(DEFAULT_PASSWORD))
        self.assertEqual(len(mail.outbox), 0)

    def test_reset_random_and_email_changes_password_and_sends_email(self):
        ResetPasswordService.reset_random_and_email(self.user)
        self.user.refresh_from_db()
        self.assertFalse(self.user.check_password("oldpass123"))
        self.assertEqual(len(mail.outbox), 1)
        self.assertIn(self.user.email, mail.outbox[0].to)
```

- [ ] **Step 2: Run tests to verify they fail**

Run: `docker-compose exec web poetry run python manage.py test users.tests.ResetPasswordServiceTest -v 2`
Expected: FAIL with `ModuleNotFoundError: No module named 'users.services'`.

- [ ] **Step 3: Create the service package and module**

Create `users/services/__init__.py` (empty file).

Create `users/services/reset_password.py`:

```python
from django.conf import settings
from django.core.mail import send_mail
from django.utils.crypto import get_random_string

DEFAULT_PASSWORD = "Zz123456"


class ResetPasswordService:

    @staticmethod
    def reset_to_default(user) -> None:
        """Сброс на фиксированный пароль без отправки письма (для админки)."""
        user.set_password(DEFAULT_PASSWORD)
        user.save(update_fields=["password"])

    @staticmethod
    def reset_random_and_email(user) -> None:
        """Сброс на случайный пароль с отправкой на email пользователя."""
        new_password = get_random_string(10)
        user.set_password(new_password)
        user.save(update_fields=["password"])
        send_mail(
            subject="Сброс пароля — Kaynaravto",
            message=f"Ваш новый пароль: {new_password}\nПожалуйста, смените его после входа.",
            from_email=settings.DEFAULT_FROM_EMAIL,
            recipient_list=[user.email],
            fail_silently=False,
        )
```

- [ ] **Step 4: Run tests to verify they pass**

Run: `docker-compose exec web poetry run python manage.py test users.tests.ResetPasswordServiceTest -v 2`
Expected: PASS (2 tests). Django's test runner uses the locmem email backend, so `mail.outbox` is populated regardless of `EMAIL_BACKEND`.

- [ ] **Step 5: Commit**

```bash
git add users/services/__init__.py users/services/reset_password.py users/tests.py
git commit -m "feat(users): add ResetPasswordService (default reset + random reset with email)"
```

---

### Task 3: Admin action to reset password

**Files:**
- Modify: `users/admin.py`
- Test: `users/tests.py`

**Interfaces:**
- Consumes: `ResetPasswordService.reset_to_default` (Task 2).

- [ ] **Step 1: Write the failing test**

Append to `users/tests.py`:

```python
from django.contrib.admin.sites import AdminSite
from django.test import RequestFactory

from users.admin import UserAdmin


class _DummyMessages:
    def add_message(self, *args, **kwargs):
        pass


class UserAdminResetActionTest(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(
            phone="+77770000002", password="oldpass123", email="u2@example.com"
        )
        self.admin = UserAdmin(User, AdminSite())
        self.request = RequestFactory().get("/admin/")
        self.request._messages = _DummyMessages()

    def test_reset_password_action_sets_default(self):
        self.admin.reset_password(self.request, User.objects.filter(pk=self.user.pk))
        self.user.refresh_from_db()
        self.assertTrue(self.user.check_password(DEFAULT_PASSWORD))
```

- [ ] **Step 2: Run test to verify it fails**

Run: `docker-compose exec web poetry run python manage.py test users.tests.UserAdminResetActionTest -v 2`
Expected: FAIL with `AttributeError: 'UserAdmin' object has no attribute 'reset_password'`.

- [ ] **Step 3: Add the action to `UserAdmin`**

In `users/admin.py`, add the import and replace the `UserAdmin` class body:

```python
from django.contrib import admin

from users.models.User import User, Role
from users.otp.models import UserCode
from users.services.reset_password import ResetPasswordService


class UserAdmin(admin.ModelAdmin):
    list_display = ('id', 'phone', 'first_name', 'email', 'status')
    actions = ['reset_password']

    @admin.action(description="Сбросить пароль на Zz123456")
    def reset_password(self, request, queryset):
        for user in queryset:
            ResetPasswordService.reset_to_default(user)
        self.message_user(request, f"Пароль сброшен у {queryset.count()} пользователей.")
```

(Leave the existing `admin.site.register(...)` lines unchanged.)

- [ ] **Step 4: Run test to verify it passes**

Run: `docker-compose exec web poetry run python manage.py test users.tests.UserAdminResetActionTest -v 2`
Expected: PASS.

- [ ] **Step 5: Commit**

```bash
git add users/admin.py users/tests.py
git commit -m "feat(users): admin action to reset password to default"
```

---

### Task 4: Public API to reset a forgotten password

**Files:**
- Modify: `users/serializers.py` (add `ResetPasswordRequestSerializer`)
- Modify: `users/views.py` (add `reset_password` method to `UserViewSet`)
- Modify: `users/urls.py` (add route)
- Test: `users/tests.py`

**Interfaces:**
- Consumes: `ResetPasswordService.reset_random_and_email` (Task 2).
- Produces: `POST /api/users/reset-password/` accepting `{"phone": "<phone>"}`.

- [ ] **Step 1: Write the failing tests**

Append to `users/tests.py`:

```python
from rest_framework.test import APIClient


class ResetPasswordAPITest(TestCase):
    def setUp(self):
        self.client = APIClient()
        self.user = User.objects.create_user(
            phone="+77770000003", password="oldpass123", email="u3@example.com"
        )
        self.no_email = User.objects.create_user(
            phone="+77770000004", password="oldpass123", email=None
        )

    def test_reset_with_valid_phone_emails_new_password(self):
        resp = self.client.post("/api/users/reset-password/", {"phone": "+77770000003"})
        self.assertEqual(resp.status_code, 200)
        self.assertEqual(len(mail.outbox), 1)
        self.user.refresh_from_db()
        self.assertFalse(self.user.check_password("oldpass123"))

    def test_reset_user_without_email_returns_400(self):
        resp = self.client.post("/api/users/reset-password/", {"phone": "+77770000004"})
        self.assertEqual(resp.status_code, 400)
        self.assertEqual(len(mail.outbox), 0)

    def test_reset_unknown_phone_returns_404(self):
        resp = self.client.post("/api/users/reset-password/", {"phone": "+77770009999"})
        self.assertEqual(resp.status_code, 404)
```

- [ ] **Step 2: Run tests to verify they fail**

Run: `docker-compose exec web poetry run python manage.py test users.tests.ResetPasswordAPITest -v 2`
Expected: FAIL (404 route not found / endpoint missing).

- [ ] **Step 3: Add the request serializer**

In `users/serializers.py`, append:

```python
class ResetPasswordRequestSerializer(serializers.Serializer):
    phone = serializers.CharField(required=True)
```

- [ ] **Step 4: Add the view method**

In `users/views.py`, add to imports:

```python
from users.serializers import ChangePasswordSerializer, ResetPasswordRequestSerializer
from users.services.reset_password import ResetPasswordService
```

(Merge with the existing `from users.serializers import ChangePasswordSerializer` line rather than duplicating it.)

Add this method to `UserViewSet` (next to `change_password`):

```python
    @swagger_auto_schema(request_body=ResetPasswordRequestSerializer)
    def reset_password(self, request):
        serializer = ResetPasswordRequestSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        phone = serializer.validated_data["phone"]
        user = User.objects.filter(phone=phone).first()
        if user is None:
            return Response({"error": "Пользователь не найден"}, status=status.HTTP_404_NOT_FOUND)
        if not user.email:
            return Response({"error": "У пользователя не указан email"},
                            status=status.HTTP_400_BAD_REQUEST)

        ResetPasswordService.reset_random_and_email(user)
        return Response({"message": "Новый пароль отправлен на email"})
```

- [ ] **Step 5: Add the route**

In `users/urls.py`, add inside `user_url` (next to the `change-password/` line):

```python
    path('reset-password/', views.UserViewSet.as_view({'post': 'reset_password'})),
```

- [ ] **Step 6: Run tests to verify they pass**

Run: `docker-compose exec web poetry run python manage.py test users.tests.ResetPasswordAPITest -v 2`
Expected: PASS (3 tests).

- [ ] **Step 7: Commit**

```bash
git add users/serializers.py users/views.py users/urls.py users/tests.py
git commit -m "feat(users): public API to reset forgotten password via email"
```

---

### Task 5: Harden the change-password API

**Files:**
- Modify: `users/views.py` (`UserViewSet.change_password` — already exists in working tree)
- Test: `users/tests.py`

**Interfaces:**
- Produces: `POST /api/users/change-password/` validates the new password against `AUTH_PASSWORD_VALIDATORS`.

- [ ] **Step 1: Write the failing tests**

Append to `users/tests.py`:

```python
class ChangePasswordAPITest(TestCase):
    def setUp(self):
        self.client = APIClient()
        self.user = User.objects.create_user(
            phone="+77770000005", password="oldpass123", email="u5@example.com"
        )
        self.client.force_authenticate(user=self.user)

    def test_change_with_valid_passwords(self):
        resp = self.client.post(
            "/api/users/change-password/",
            {"old_password": "oldpass123", "new_password": "BrandNew987"},
        )
        self.assertEqual(resp.status_code, 200)
        self.user.refresh_from_db()
        self.assertTrue(self.user.check_password("BrandNew987"))

    def test_change_with_wrong_old_password_returns_400(self):
        resp = self.client.post(
            "/api/users/change-password/",
            {"old_password": "WRONG", "new_password": "BrandNew987"},
        )
        self.assertEqual(resp.status_code, 400)

    def test_change_with_weak_new_password_returns_400(self):
        resp = self.client.post(
            "/api/users/change-password/",
            {"old_password": "oldpass123", "new_password": "123"},
        )
        self.assertEqual(resp.status_code, 400)
        self.user.refresh_from_db()
        self.assertTrue(self.user.check_password("oldpass123"))
```

- [ ] **Step 2: Run tests to verify the weak-password test fails**

Run: `docker-compose exec web poetry run python manage.py test users.tests.ChangePasswordAPITest -v 2`
Expected: `test_change_with_weak_new_password_returns_400` FAILS (current code accepts `123`, returns 200).

- [ ] **Step 3: Add password validation to `change_password`**

In `users/views.py`, add the import:

```python
from django.contrib.auth.password_validation import validate_password
from django.core.exceptions import ValidationError as DjangoValidationError
```

Replace the body of `change_password` so validation runs before setting the password:

```python
    @swagger_auto_schema(request_body=ChangePasswordSerializer)
    def change_password(self, request):
        serializer = ChangePasswordSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        user = request.user
        old_password = serializer.validated_data["old_password"]
        new_password = serializer.validated_data["new_password"]

        if not user.check_password(old_password):
            return Response({"error": "Неправильный пароль"}, status=status.HTTP_400_BAD_REQUEST)

        try:
            validate_password(new_password, user=user)
        except DjangoValidationError as e:
            return Response({"error": e.messages}, status=status.HTTP_400_BAD_REQUEST)

        user.set_password(new_password)
        user.save()

        return Response({"message": "Пароль успешно изменен"})
```

- [ ] **Step 4: Run tests to verify they pass**

Run: `docker-compose exec web poetry run python manage.py test users.tests.ChangePasswordAPITest -v 2`
Expected: PASS (3 tests).

- [ ] **Step 5: Run the full users test suite**

Run: `docker-compose exec web poetry run python manage.py test users -v 2`
Expected: PASS (all tests from Tasks 2–5).

- [ ] **Step 6: Commit**

```bash
git add users/views.py users/tests.py
git commit -m "feat(users): validate new password on change-password endpoint"
```

---

## Notes for the implementer

- `force_authenticate` bypasses the custom `CustomJWTAuthentication`, so no real JWT is needed in tests.
- If `manage.py check` or tests can't reach Postgres, ensure the stack is up: `docker-compose up -d db web`.
- Do not stage the branch's pre-existing unrelated changes; `git add` only the exact paths listed per task.
