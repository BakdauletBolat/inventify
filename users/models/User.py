import uuid

from django.contrib.auth.models import AbstractBaseUser, PermissionsMixin, Permission
from django.db import models
from django.db.models import IntegerChoices
from django.utils import timezone

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


class Role(models.Model):
    name = models.CharField(max_length=255, unique=True)
    description = models.TextField(blank=True, null=True)

    def __str__(self):
        return self.name


def gen_uuid():
    return uuid.uuid4()


class User(AbstractBaseUser, PermissionsMixin):
    phone = fields.PhoneField(unique=True)
    uuid = models.UUIDField(default=gen_uuid, editable=False, unique=True, null=True, blank=True)
    email = models.EmailField(null=True, blank=True, max_length=255)
    first_name = models.CharField('Имя', max_length=255)
    last_name = models.CharField('Фамилия', max_length=255)
    middle_name = models.CharField('Отчество', max_length=255, null=True, blank=True)
    roles = models.ManyToManyField(Role, verbose_name='Роли', related_name='users')
    city = models.ForeignKey(City, on_delete=models.CASCADE, related_name='users', null=True, blank=True,
                             verbose_name='Город')

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
