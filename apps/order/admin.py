from django.contrib import admin
from apps.order import models

# Register your models here.
admin.site.register(models.Order)
admin.site.register(models.OrderItem)
