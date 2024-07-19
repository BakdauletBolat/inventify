from django.contrib import admin

from apps.product.enums import StatusChoices
# Register your models here.
from apps.stock import models


class WarehouseAdmin(admin.ModelAdmin):
    list_display = ('id', 'name', 'min_stock_level', 'get_stock')
    search_fields = ('name', )

    def get_stock(self, warehouse: models.Warehouse):
        return warehouse.stock_set.filter(product__status=StatusChoices.IN_STOCK).count()


admin.site.register(models.Warehouse, WarehouseAdmin)


class StockAdmin(admin.ModelAdmin):
    list_display = ('id', 'product', 'warehouse', 'quality', 'quantity')

    def has_delete_permission(self, request, obj=None):
        return False

    def has_add_permission(self, request):
        return False

    def has_change_permission(self, request, obj=None):
        return False


class StockHistoryAdmin(admin.ModelAdmin):
    list_display = ('id', 'stock', 'quantity_before', 'quantity_after',)


admin.site.register(models.Stock, StockAdmin)
admin.site.register(models.Quality)
admin.site.register(models.StockHistory, StockHistoryAdmin)
admin.site.register(models.StockMovement)
