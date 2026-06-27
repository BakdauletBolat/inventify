from django.contrib import admin

from users.models.User import User, Role
from users.otp.models import UserCode
from users.services.reset_password import ResetPasswordService


class UserAdmin(admin.ModelAdmin):
    list_display = ('id', 'phone', 'first_name', 'email', 'status')
    actions = ['reset_password']

    @admin.action(description="Сбросить пароль на Zz123456")
    def reset_password(self, request, queryset):
        for user in queryset:
            ResetPasswordService.reset_to_default(user)
        self.message_user(request, f"Пароль сброшен у {queryset.count()} пользователей.")


# Register your models here.
admin.site.register(User, UserAdmin)
admin.site.register(Role)
admin.site.register(UserCode)
