from django.contrib.auth.models import AbstractUser
from django.db import models
from django.db.models import IntegerChoices

from base import models as base_models
from handbook.models import City
from users import fields
from users import managers


class PROFILE_TYPES(IntegerChoices):
    SUPERVISOR = (
        1,
        "Супервизор",
    )
    EMPLOYEE = (
        2,
        "Сотрудник"
    )
    SELLER = (
        3,
        "Продавец",
    )
    CLIENT = (
        4,
        "Клиент"
    )


class User(AbstractUser):
    phone = fields.PhoneField(unique=True)
    email = models.EmailField(null=True, blank=True, max_length=255)
    first_name = models.CharField('Имя', max_length=255)
    last_name = models.CharField('Фамилия', max_length=255)
    middle_name = models.CharField('Отчество', max_length=255, null=True, blank=True)

    profile_type = models.IntegerField(choices=PROFILE_TYPES.choices, default=PROFILE_TYPES.CLIENT, max_length=100)
    city = models.ForeignKey(City, on_delete=models.CASCADE, related_name='users', null=True, blank=True,
                             verbose_name='Город')
    postcode = models.CharField('Почтовый индекс', max_length=255, null=True, blank=True)

    is_staff = models.BooleanField(default=False)
    is_superuser = models.BooleanField(default=False)
    USERNAME_FIELD = 'phone'

    username = None

    manager = managers.UserManager()


class SupervisorProfile(base_models.BaseModel):
    user = models.ForeignKey(User, on_delete=models.CASCADE)


class EmployeeProfile(base_models.BaseModel):
    user = models.ForeignKey(User, on_delete=models.CASCADE)


class SellerProfile(base_models.BaseModel):
    user = models.ForeignKey(User, on_delete=models.CASCADE)


class ClientProfile(base_models.BaseModel):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
