from django.contrib import admin
from django.db.models import JSONField
from django_json_widget.widgets import JSONEditorWidget

from apps.car.models import ModificationDraft
from apps.car.models.Model import *
from apps.car.models.Modification import Modification, Engine


class ModelCarAdmin(admin.ModelAdmin):
    list_display = ('id', 'name', 'manufacturer_id')
    list_filter = ('manufacturer_id',)


class ManufacturerTypeAdmin(admin.ModelAdmin):
    list_display = ('id', 'name')


class ModificationAdmin(admin.ModelAdmin):
    list_display = ('id', 'name', 'modelCar')
    list_filter = ('modelCar__manufacturer',)


class ModificationDraftAdmin(admin.ModelAdmin):
    search_fields = ('product_id',)
    formfield_overrides = {
        JSONField: {'widget': JSONEditorWidget},
    }


class EngineAdmin(admin.ModelAdmin):
    search_fields = ('name',)
    raw_id_fields = ('modification',)
    search_fields = ('name', )


admin.site.register(Modification, ModificationAdmin)
admin.site.register(ModelCar, ModelCarAdmin)
admin.site.register(Engine, EngineAdmin)
admin.site.register(ManufacturerType, ManufacturerTypeAdmin)
admin.site.register(ModificationDraft, ModificationDraftAdmin)
