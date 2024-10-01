from base.repository import BaseRepository
from users.models.User import *


class UserRepository(BaseRepository):
    model = User

    @classmethod
    def create(cls, **kwargs):
        user = None
        # user = cls.model.objects.create(**kwargs)
        match kwargs['profile_type']:
            case PROFILE_TYPES.SUPERVISOR:
                user = SupervisorProfile.objects.create(**kwargs)
                user.is_superuser = True
                user.save()
            case PROFILE_TYPES.CLIENT:
                user = ClientProfile.objects.create(**kwargs)
            case PROFILE_TYPES.SELLER:
                user = SellerProfile.objects.create(**kwargs)
            case PROFILE_TYPES.EMPLOYEE:
                user = EmployeeProfile.objects.create(**kwargs)
        return user
