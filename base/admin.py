from django.contrib import admin
from django.db.models import JSONField
from django_json_widget.widgets import JSONEditorWidget

from base.models import RecarRequestLog


@admin.register(RecarRequestLog)
class RecarRequestLogAdmin(admin.ModelAdmin):
    """Только просмотр: строки пишет интеграция, руками их не создают и не правят."""

    list_display = ('created_at', 'operation_name', 'status_code', 'duration_ms', 'is_failed')
    list_filter = ('operation_name', 'status_code')
    search_fields = ('operation_name', 'error')
    date_hierarchy = 'created_at'
    readonly_fields = (
        'created_at', 'operation_name', 'status_code', 'duration_ms',
        'query', 'variables', 'response', 'error',
    )
    formfield_overrides = {
        JSONField: {'widget': JSONEditorWidget},
    }

    @admin.display(description='Ошибка', boolean=True)
    def is_failed(self, obj: RecarRequestLog):
        return bool(obj.error) or (obj.status_code or 0) >= 400

    def has_add_permission(self, request):
        return False

    def has_change_permission(self, request, obj=None):
        return False
