from django.contrib import admin
from .models import HourLog, WeeklyLog


@admin.register(HourLog)
class HourLogAdmin(admin.ModelAdmin):
    """Admin interface for HourLog model."""
    list_display = ('intern', 'date', 'total_hours', 'status', 'created_at')
    list_filter = ('status', 'date', 'intern')
    search_fields = ('intern__email', 'intern__first_name', 'description')
    readonly_fields = ('created_at', 'updated_at')
    fieldsets = (
        ('Entry Information', {
            'fields': ('intern', 'date', 'time_in', 'time_out', 'description')
        }),
        ('Review Information', {
            'fields': ('status', 'reviewed_by', 'review_notes')
        }),
        ('Timestamps', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )


@admin.register(WeeklyLog)
class WeeklyLogAdmin(admin.ModelAdmin):
    """Admin interface for WeeklyLog model."""
    list_display = ('intern', 'week_start', 'week_end', 'total_hours')
    list_filter = ('week_start', 'intern')
    search_fields = ('intern__email', 'intern__first_name')
    readonly_fields = ('created_at', 'updated_at')
