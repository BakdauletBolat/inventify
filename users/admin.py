from django.contrib import admin

from users.models.User import User, Role
from users.otp.models import UserCode


class UserAdmin(admin.ModelAdmin):
    list_display = ('id', 'phone', 'first_name', 'status')


# Register your models here.
admin.site.register(User, UserAdmin)
admin.site.register(Role)
admin.site.register(UserCode)
