from django.db import models
from django.contrib.auth.models import AbstractUser
from django.db.models import TextChoices
from base import models as base_models

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
    phone = fields.PhoneField()
    profile_type = models.CharField(choices=PROFILE_TYPES, default=PROFILE_TYPES.CLIENT)
    email = models.EmailField(null=True, blank=True)


class SupervisorProfile(base_models.BaseModel):
    name = models.Charfield(null=True, blank=True)
    first_name = models.CharField(null=True, blank=True)
