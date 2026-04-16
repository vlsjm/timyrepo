from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from .models import CustomUser, InternProfile, SupervisorProfile, AdminProfile, DaySchedule


class CustomUserAdmin(UserAdmin):
    """Admin interface for CustomUser model."""
    model = CustomUser
    list_display = ('email', 'first_name', 'last_name', 'role', 'is_staff')
    list_filter = ('role', 'is_staff', 'is_active', 'groups')
    fieldsets = (
        (None, {'fields': ('email', 'password', 'username', 'role')}),
        ('Personal info', {'fields': ('first_name', 'last_name')}),
        ('Permissions', {
            'fields': ('is_active', 'is_staff', 'is_superuser', 'groups', 'user_permissions'),
        }),
        ('Important dates', {'fields': ('last_login', 'date_joined')}),
    )
    add_fieldsets = (
        (None, {
            'classes': ('wide',),
            'fields': ('email', 'password1', 'password2', 'role'),
        }),
    )
    search_fields = ('email', 'first_name', 'last_name')
    ordering = ('email',)


@admin.register(InternProfile)
class InternProfileAdmin(admin.ModelAdmin):
    """Admin interface for InternProfile model."""
    list_display = ('user', 'company', 'course', 'required_hours')
    list_filter = ('company', 'course')
    search_fields = ('user__email', 'user__first_name', 'company')
    readonly_fields = ('created_at', 'updated_at')


@admin.register(SupervisorProfile)
class SupervisorProfileAdmin(admin.ModelAdmin):
    """Admin interface for SupervisorProfile model."""
    list_display = ('user', 'department')
    list_filter = ('department',)
    search_fields = ('user__email', 'user__first_name')
    readonly_fields = ('created_at', 'updated_at')


@admin.register(AdminProfile)
class AdminProfileAdmin(admin.ModelAdmin):
    """Admin interface for AdminProfile model."""
    list_display = ('user',)
    search_fields = ('user__email', 'user__first_name')
    readonly_fields = ('created_at', 'updated_at')


@admin.register(DaySchedule)
class DayScheduleAdmin(admin.ModelAdmin):
    """Admin interface for DaySchedule model."""
    list_display = ('user', 'day_of_week', 'is_working_day', 'start_time', 'end_time')
    list_filter = ('day_of_week', 'is_working_day')
    search_fields = ('user__email', 'user__first_name')
    readonly_fields = ('created_at', 'updated_at')


admin.site.register(CustomUser, CustomUserAdmin)
