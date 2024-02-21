from django.contrib import admin

from apps.product.models.Price import Price
from apps.product.models.Product import *


class ProductImageTabularInline(admin.TabularInline):
    model = ProductImage
    extra = 0


class ProductDetailTabularInline(admin.TabularInline):
    model = ProductDetail
    extra = 0


class PriceTabularInline(admin.TabularInline):
    model = Price
    extra = 0


class ProductAdmin(admin.ModelAdmin):
    list_display = ('id', 'name', 'get_last_price')
    raw_id_fields = ('modification',)
    inlines = [ProductImageTabularInline, ProductDetailTabularInline, PriceTabularInline]

    def get_last_price(self, product):
        return product.price.last()


admin.site.register(Price)
admin.site.register(Product, ProductAdmin)
admin.site.register(ProductImage)
admin.site.register(ProductDetail)
