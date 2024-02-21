from django.contrib import admin
from apps.category import models


class CategoryAdmin(admin.ModelAdmin):
    list_display = ('id', 'name', 'parent_id',)
    list_filter = ('parent_id',)


admin.site.register(models.Category, CategoryAdmin)