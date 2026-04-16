from django.contrib import admin
from .models import Report


@admin.register(Report)
class ReportAdmin(admin.ModelAdmin):
    """Admin interface for Report model."""
    list_display = ('intern', 'report_type', 'format', 'start_date', 'end_date', 'created_at')
    list_filter = ('report_type', 'format', 'created_at')
    search_fields = ('intern__email', 'intern__first_name')
    readonly_fields = ('created_at',)
