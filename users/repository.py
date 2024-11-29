from base.repository import BaseRepository
from users.models.User import *


class UserRepository(BaseRepository):
    model = User

    @classmethod
    def create(cls, **kwargs):
        roles = kwargs.pop('roles', [])
        user = cls.model.objects.create(**kwargs)
        user.roles.set(roles)
        return user
