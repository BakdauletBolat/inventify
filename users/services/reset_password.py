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
