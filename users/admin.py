from django.contrib import admin

from users.models.User import User
from users.models.Address import Address

# Register your models here.
admin.site.register(User)
admin.site.register(Address)