from users.models.User import User
from users.repository import UserRepository
from users.serializers import UserRegisterSerializer


class CreateUserAction:

    def __init__(self, data: UserRegisterSerializer.data):
        self.data = data

    def run(self) -> User:
        user = UserRepository.create(**self.data)
        return user
