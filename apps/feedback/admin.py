from django.contrib import admin

from apps.feedback.models import Feedback


class FeedbackAdmin(admin.ModelAdmin):
    list_display = ('phone', 'name', 'completed_at')
    list_filter = ('name', 'completed_at', 'phone')


admin.site.register(Feedback, FeedbackAdmin)
