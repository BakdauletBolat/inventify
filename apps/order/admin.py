from django.contrib import admin

from apps.order import models
from apps.order.models import OrderItem


class OrderItemTabularInline(admin.TabularInline):
    model = OrderItem
    extra = 0


class OrderAdmin(admin.ModelAdmin):
    list_display = ('id', 'total', 'payment_type', 'payment_status', 'status')
    list_filter = ('payment_type', 'payment_status', 'status')
    inlines = [OrderItemTabularInline]


admin.site.register(models.Order, OrderAdmin)
admin.site.register(models.OrderItem)
