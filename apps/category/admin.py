from django.contrib import admin

from apps.category import models
from apps.product.models.Product import Product


class GrandchildInline(admin.TabularInline):
    model = Product
    extra = 0
    fields = ('name',)


class ChildInline(admin.TabularInline):
    model = models.Category
    fields = ('id', 'name', 'recar_category_id')  # Убираем 'children' из fields
    extra = 1


class CategoryAdmin(admin.ModelAdmin):
    inlines = [ChildInline, GrandchildInline]
    list_display = ('id', 'name', 'parent', 'recar_category_id')
    list_filter = ('parent_id',)
    ordering = ('parent_id',)
    search_fields = ('name', )


admin.site.register(models.Category, CategoryAdmin)
