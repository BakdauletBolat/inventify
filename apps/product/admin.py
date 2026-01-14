from django import forms
from django.contrib import admin
from django.contrib.admin.widgets import AdminFileWidget, AdminURLFieldWidget
from django.db.models import JSONField
from django.urls import reverse
from django.utils.html import format_html
from django_json_widget.widgets import JSONEditorWidget
from djangoql.admin import DjangoQLSearchMixin
from eav.forms import BaseDynamicEntityForm

from apps.car.models import ModelCar, Engine
from apps.product.actions import ImportProductAction
from apps.product.models import ImportProductData
from apps.product.models.Price import Price
from apps.product.models.Product import *
from apps.product.tasks import import_pictures_from_recar


class ProductAdminForm(BaseDynamicEntityForm):
    modelCar = forms.ModelChoiceField(
        queryset=ModelCar.objects.all(),
        required=False,
        label='Модель машины',
        widget=AdminURLFieldWidget(attrs={'class': 'vForeignKeyRawIdAdminField'})
    )

    engine = forms.ModelChoiceField(
        queryset=Engine.objects.all(),
        required=False,
        label='Двигатель',
        widget=AdminURLFieldWidget(attrs={'class': 'vForeignKeyRawIdAdminField'})
    )

    class Meta:
        model = Product
        fields = '__all__'

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Убедитесь, что поля корректно настроены для отображения
        if self.instance:
            model_car = getattr(self.instance.eav, 'modelCar', None)
            engine = getattr(self.instance.eav, 'engine', None)
            self.fields['modelCar'].initial = model_car
            self.fields['engine'].initial = engine

            if model_car:
                url = reverse('admin:car_modelcar_change', args=[model_car.pk])
                self.fields['modelCar'].help_text = format_html('<a href="{}">Перейти к модели машины</a>', url)

            if engine:
                url = reverse('admin:car_modelcar_change', args=[engine.pk])
                self.fields['engine'].help_text = format_html('<a href="{}">Перейти к двигателю</a>', url)

    def clean(self):
        cleaned_data = super().clean()
        # Обработка данных полей EAV при сохранении
        model_car = cleaned_data.get('modelCar')
        engine = cleaned_data.get('engine')
        if model_car:
            self.instance.eav.modelCar = model_car
        if engine:
            self.instance.eav.engine = engine
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


class ProductComponents(admin.TabularInline):
    model = Product
    extra = 0
    raw_id_fields = ('modification', 'parent',)
    fields = ('name', 'category', 'status', 'warehouse',)


@admin.action(description='Импортировать фото')
def import_photos_from_recar(modeladmin, request, queryset: Product):
    for obj in queryset:
        import_pictures_from_recar.delay(obj.id)
        

class ProductAdmin(DjangoQLSearchMixin, admin.ModelAdmin):
    actions = [import_photos_from_recar]
    form = ProductAdminForm
    search_fields = ('name',)
    list_display = ('id', 'name', 'status')
    raw_id_fields = ('modification', 'parent',)
    list_filter = ('status',)
    inlines = [ProductComponents, ProductImageTabularInline, ProductDetailTabularInline, PriceTabularInline]

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


class ProductImageAdmin(admin.ModelAdmin):
    list_display = ('product_id', 'id')
    raw_id_fields = ('product',)


class PriceAdmin(DjangoQLSearchMixin, admin.ModelAdmin):
    raw_id_fields = ('product',)
    list_display = ('cost', 'product')


admin.site.register(Price, PriceAdmin)
admin.site.register(Product, ProductAdmin)
admin.site.register(ProductView)
admin.site.register(ImportProductData, ImportProductAdmin)
admin.site.register(ProductImage, ProductImageAdmin)
admin.site.register(ProductDetail)
