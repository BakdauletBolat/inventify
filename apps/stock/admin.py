from django.contrib import admin

# Register your models here.
from apps.stock import models

admin.site.register(models.Warehouse)


class StockAdmin(admin.ModelAdmin):

    def has_delete_permission(self, request, obj=None):
        return False

    def has_add_permission(self, request):
        return False

    def has_change_permission(self, request, obj=None):
        return False


admin.site.register(models.Stock, StockAdmin)
admin.site.register(models.Quality)
admin.site.register(models.StockHistory)
admin.site.register(models.StockReceipt)
