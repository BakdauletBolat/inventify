from django.db import models
from django.contrib.auth.models import AbstractUser
from django.db.models import TextChoices
from base import models as base_models
from users import managers
from users import fields


class PROFILE_TYPES(TextChoices):
    SUPERVISOR = (
        "SUPERVISOR",
        "Супервизор",
    )
    SELLER = (
        "SELLER",
        "Продавец",
    )
    CLIENT = (
        "CLIENT",
        "Клиент"
    )


class User(AbstractUser):
    phone = fields.PhoneField(unique=True)
    profile_type = models.CharField(choices=PROFILE_TYPES.choices, default=PROFILE_TYPES.CLIENT, max_length=100)
    email = models.EmailField(null=True, blank=True, max_length=255)
    is_staff = models.BooleanField(default=False)
    is_superuser = models.BooleanField(default=False)
    USERNAME_FIELD = 'phone'

    username = None

    manager = managers.UserManager()


class SupervisorProfile(base_models.BaseModel):
    name = models.CharField(null=True, blank=True, max_length=255)
    first_name = models.CharField(null=True, blank=True, max_length=255)
