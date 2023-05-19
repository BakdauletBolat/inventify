from django.contrib.auth.models import BaseUserManager


class UserManager(BaseUserManager):

    @staticmethod
    def normalize_phone(phone):
        return phone

    def create_user(self, phone, password=None, **extra_fields):
        phone = self.normalize_phone(phone)
        user = self.model(phone=phone, **extra_fields)
        user.set_password(password)
        user.save(using=self._db)
        return user

    def create_superuser(self, phone, password=None, **extra_fields):
        extra_fields.setdefault('is_staff', True)
        extra_fields.setdefault('is_superuser', True)
        return self.create_user(phone, password, **extra_fields)
