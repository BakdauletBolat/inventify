from django.contrib import admin
from django.contrib.admin.widgets import AdminFileWidget
from django.db.models import JSONField
from django.utils.html import format_html
from django_json_widget.widgets import JSONEditorWidget

from apps.product.models import ImportProductData
from apps.product.models.Price import Price
from apps.product.models.Product import *


class AdminImageWidget(AdminFileWidget):
    def render(self, name, value, attrs=None, renderer=None):
        result = []
        if hasattr(value, "url"):
            result.append(
                f'''<a href="{value.url}" target="_blank">
                      <img 
                        src="{value.url}" alt="{value}" 
                        width="100" height="100"
                        style="object-fit: cover;"
                      />
                    </a>'''
            )
        result.append(super().render(name, value, attrs, renderer))
        return format_html("".join(result))


class ProductImageTabularInline(admin.StackedInline):
    model = ProductImage
    extra = 0
    formfield_overrides = {
        models.ImageField: {'widget': AdminImageWidget}
    }


class ProductDetailTabularInline(admin.TabularInline):
    model = ProductDetail
    extra = 0


class PriceTabularInline(admin.TabularInline):
    model = Price
    extra = 0


class ProductAdmin(admin.ModelAdmin):
    list_display = ('id', 'name', 'get_last_price', 'status')
    raw_id_fields = ('modification',)
    inlines = [ProductImageTabularInline, ProductDetailTabularInline, PriceTabularInline]

    def get_last_price(self, product):
        return product.price.last()


class ImportProductAdmin(admin.ModelAdmin):
    search_fields = ('product_id', )
    formfield_overrides = {
        JSONField: {'widget': JSONEditorWidget},
    }


admin.site.register(Price)
admin.site.register(Product, ProductAdmin)
admin.site.register(ImportProductData, ImportProductAdmin)
admin.site.register(ProductImage)
admin.site.register(ProductDetail)
