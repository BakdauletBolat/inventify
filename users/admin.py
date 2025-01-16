from django.contrib import admin

from users.models.User import User, Role
from users.otp.models import UserCode

# Register your models here.
admin.site.register(User)
admin.site.register(Role)
admin.site.register(UserCode)
