from base.repository import BaseRepository
from users.models.User import *


class UserRepository(BaseRepository):
    model = User

    @classmethod
    def create(cls, **kwargs):
        user = cls.model.objects.create(**kwargs)
        match kwargs['profile_type']:
            case PROFILE_TYPES.SUPERVISOR:
                user.is_superuser = True
                user.save()
                SupervisorProfile.objects.create(user=user)
            case PROFILE_TYPES.CLIENT:
                ClientProfile.objects.create(user=user)
            case PROFILE_TYPES.SELLER:
                SellerProfile.objects.create(user=user)
            case PROFILE_TYPES.EMPLOYEE:
                EmployeeProfile.objects.create(user=user)
        return user