from django import forms
from django.contrib import admin
from django.contrib.admin.widgets import AdminFileWidget
from django.db.models import JSONField
from django.utils.html import format_html
from django_json_widget.widgets import JSONEditorWidget
from eav.admin import BaseEntityAdmin
from eav.forms import BaseDynamicEntityForm

from apps.car.models import ModelCar
from apps.product.actions import ImportProductAction
from apps.product.models import ImportProductData
from apps.product.models.Price import Price
from apps.product.models.Product import *


class ProductAdminForm(BaseDynamicEntityForm):
    modelCar = forms.ModelChoiceField(
        queryset=ModelCar.objects.all(),
        required=False,
        label='Модель машины'
    )

    class Meta:
        model = Product
        fields = '__all__'

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Убедитесь, что поля корректно настроены для отображения
        if self.instance:
            self.fields['modelCar'].initial = self.instance.eav.modelCar

    def clean(self):
        cleaned_data = super().clean()
        # Обработка данных полей EAV при сохранении
        model_car = cleaned_data.get('modelCar')
        if model_car:
            self.instance.eav.modelCar = model_car
        return cleaned_data


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


class ProductAdmin(BaseEntityAdmin):
    form = ProductAdminForm
    list_display = ('id', 'name', 'get_last_price', 'status')
    raw_id_fields = ('modification',)
    list_filter = ('status',)
    inlines = [ProductImageTabularInline, ProductDetailTabularInline, PriceTabularInline]

    def get_last_price(self, product):
        return product.price.last()


@admin.action(description='Импортировать в основную базу продуктов')
def import_from_recar(modeladmin, request, queryset: ImportProductData):
    for obj in queryset:
        ImportProductAction().run(obj.data)


class ImportProductAdmin(admin.ModelAdmin):
    actions = [import_from_recar]
    search_fields = ('product_id',)
    formfield_overrides = {
        JSONField: {'widget': JSONEditorWidget},
    }


admin.site.register(Price)
admin.site.register(Product, ProductAdmin)
admin.site.register(ImportProductData, ImportProductAdmin)
admin.site.register(ProductImage)
admin.site.register(ProductDetail)
