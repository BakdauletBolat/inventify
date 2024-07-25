from django.contrib import admin

from apps.product.enums import StatusChoices
# Register your models here.
from apps.stock import models


class StockTabularInline(admin.TabularInline):
    model = models.Stock
    readonly_fields = ('product',)
    extra = 0


class WarehouseAdmin(admin.ModelAdmin):
    list_display = ('id', 'name', 'min_stock_level', 'get_stock')
    search_fields = ('name',)
    filter_horizontal = ('products_category',)
    inlines = [StockTabularInline, ]

    def get_stock(self, warehouse: models.Warehouse):
        return warehouse.stock_set.filter(product__status=StatusChoices.IN_STOCK).count()


admin.site.register(models.Warehouse, WarehouseAdmin)


class StockAdmin(admin.ModelAdmin):
    list_display = ('id', 'product', 'product_id', 'warehouse', 'quality', 'quantity')

    def has_delete_permission(self, request, obj=None):
        return False

    def has_add_permission(self, request):
        return False

    def has_change_permission(self, request, obj=None):
        return False


class StockMovementAdmin(admin.ModelAdmin):
    raw_id_fields = ('product', 'warehouse',)


admin.site.register(models.Stock, StockAdmin)
admin.site.register(models.Quality)
admin.site.register(models.StockMovement, StockMovementAdmin)
