from django.contrib.auth.models import AbstractBaseUser
from django.db import models
from django.db.models import IntegerChoices
from django.utils import timezone

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


class User(AbstractBaseUser):
    phone = fields.PhoneField(unique=True)
    email = models.EmailField(null=True, blank=True, max_length=255)
    first_name = models.CharField('Имя', max_length=255)
    last_name = models.CharField('Фамилия', max_length=255)
    middle_name = models.CharField('Отчество', max_length=255, null=True, blank=True)

    profile_type = models.IntegerField(choices=PROFILE_TYPES.choices, default=PROFILE_TYPES.CLIENT)
    city = models.ForeignKey(City, on_delete=models.CASCADE, related_name='users', null=True, blank=True,
                             verbose_name='Город')
    postcode = models.CharField('Почтовый индекс', max_length=255, null=True, blank=True)

    is_active = models.BooleanField(default=True)
    is_staff = models.BooleanField(default=False)
    is_superuser = models.BooleanField(default=False)
    date_joined = models.DateTimeField(default=timezone.now)

    USERNAME_FIELD = 'phone'

    objects = managers.UserManager()

    def __str__(self):
        return self.phone

    def get_full_name(self):
        return f'{self.first_name} {self.last_name}'

    def get_short_name(self):
        return self.first_name

    def has_perm(self, perm, obj=None):
        return self.is_superuser

    def has_module_perms(self, app_label):
        return self.is_superuser


class SupervisorProfile(base_models.BaseModel):
    user = models.ForeignKey(User, on_delete=models.CASCADE)


class EmployeeProfile(base_models.BaseModel):
    user = models.ForeignKey(User, on_delete=models.CASCADE)


class SellerProfile(base_models.BaseModel):
    user = models.ForeignKey(User, on_delete=models.CASCADE)


class ClientProfile(base_models.BaseModel):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
