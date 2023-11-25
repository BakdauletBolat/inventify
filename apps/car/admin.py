from django.contrib import admin

from apps.car.models.Model import *
from apps.car.models.Modification import Modification


class ModelCarAdmin(admin.ModelAdmin):
    list_display = ('id', 'name', 'manufacturer_id')
    list_filter = ('manufacturer_id',)


class ManufacturerTypeAdmin(admin.ModelAdmin):
    list_display = ('id', 'name')


class ModificationAdmin(admin.ModelAdmin):
    list_display = ('id', 'name', 'modelCar')
    list_filter = ('modelCar__manufacturer',)


admin.site.register(Modification, ModificationAdmin)
admin.site.register(ModelCar, ModelCarAdmin)
admin.site.register(ManufacturerType, ManufacturerTypeAdmin)
