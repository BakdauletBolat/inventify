from django.core.management import BaseCommand

from base.requests import RecarRequest
from users.models.User import User, Role


class Command(BaseCommand):
    help = "seed database for testing and development."

    def handle(self, *args, **options):
        self.stdout.write('import users...')
        users = RecarRequest().get_users()
        i = ''
        number = 1

        for user in users:

            user_obj, created = User.objects.update_or_create(
                uuid=user['id'],
                defaults={
                    'first_name': user['firstname'],
                    'last_name': user['lastname'],
                    'phone': user['phoneNumber'] + i if user['phoneNumber'] == '+77021755757' else user['phoneNumber'],
                    'email': user['email'],
                }

            )

            roles = []
            for role in user['roles']:
                role, created = Role.objects.get_or_create(
                    id=role['id'],
                    defaults={
                        "name": role['name']
                    }
                )
                roles.append(role)

            user_obj.roles.set(roles)
            number += 1
            i = f'({number})'
        self.stdout.write('done.')
