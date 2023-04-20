from django.contrib import admin

# Register your models here.
from apps.stock import models

admin.site.register(models.Warehouse)
admin.site.register(models.Stock)
admin.site.register(models.Quality)
