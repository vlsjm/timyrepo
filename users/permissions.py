"""
Permissions utilities for role-based access control.
Provides helper functions and decorators for permission checking.
"""
from functools import wraps
from django.shortcuts import redirect
from django.contrib import messages


def has_permission(user, permission_codename):
    """
    Check if user has a specific permission.
    
    Args:
        user: Django user object
        permission_codename: String codename (e.g., 'log_hours', 'approve_logs')
    
    Returns:
        Boolean indicating if user has permission
    """
    if user.is_superuser:
        return True
    return user.has_perm(f'logging_app.{permission_codename}')


def has_any_permission(user, permission_codenames):
    """
    Check if user has any of the specified permissions.
    
    Args:
        user: Django user object
        permission_codenames: List of permission codenames
    
    Returns:
        Boolean indicating if user has any permission
    """
    if user.is_superuser:
        return True
    return any(
        user.has_perm(f'logging_app.{perm}')
        for perm in permission_codenames
    )


def has_all_permissions(user, permission_codenames):
    """
    Check if user has all of the specified permissions.
    
    Args:
        user: Django user object
        permission_codenames: List of permission codenames
    
    Returns:
        Boolean indicating if user has all permissions
    """
    if user.is_superuser:
        return True
    return all(
        user.has_perm(f'logging_app.{perm}')
        for perm in permission_codenames
    )


def check_permission(permission_codename, redirect_url='dashboard'):
    """
    Decorator to check if user has permission before accessing view.
    Redirects to specified URL if permission denied.
    
    Usage:
        @check_permission('log_hours')
        def log_hours(request):
            ...
    """
    def decorator(view_func):
        @wraps(view_func)
        def wrapper(request, *args, **kwargs):
            if not request.user.is_authenticated:
                messages.error(request, 'Please log in first.')
                return redirect('users:login')
            
            if not has_permission(request.user, permission_codename):
                messages.error(request, 'You do not have permission to access this page.')
                return redirect(redirect_url)
            
            return view_func(request, *args, **kwargs)
        return wrapper
    return decorator


def check_any_permission(permission_codenames, redirect_url='dashboard'):
    """
    Decorator to check if user has any of the specified permissions.
    
    Usage:
        @check_any_permission(['approve_logs', 'reject_logs'])
        def review_logs(request):
            ...
    """
    def decorator(view_func):
        @wraps(view_func)
        def wrapper(request, *args, **kwargs):
            if not request.user.is_authenticated:
                messages.error(request, 'Please log in first.')
                return redirect('users:login')
            
            if not has_any_permission(request.user, permission_codenames):
                messages.error(request, 'You do not have permission to access this page.')
                return redirect(redirect_url)
            
            return view_func(request, *args, **kwargs)
        return wrapper
    return decorator


def is_intern(user):
    """Check if user belongs to Intern group."""
    if user.is_superuser:
        return True
    return user.groups.filter(name='Intern').exists()


def is_supervisor(user):
    """Check if user belongs to Supervisor group."""
    if user.is_superuser:
        return True
    return user.groups.filter(name='Supervisor').exists()


def is_admin(user):
    """Check if user is admin (superuser or Admin group)."""
    return user.is_superuser or user.groups.filter(name='Admin').exists()


def user_can_log_hours(user):
    """Check if user can log hours."""
    return user.has_perm('logging_app.log_hours')


def user_can_view_own_logs(user):
    """Check if user can view own logs."""
    return user.has_perm('logging_app.view_own_logs')


def user_can_edit_own_logs(user):
    """Check if user can edit own logs."""
    return user.has_perm('logging_app.edit_own_logs')


def user_can_approve_logs(user):
    """Check if user can approve logs."""
    return user.has_perm('logging_app.approve_logs')


def user_can_view_all_logs(user):
    """Check if user can view all logs."""
    return user.has_perm('logging_app.view_all_logs')


def user_can_generate_reports(user):
    """Check if user can generate reports."""
    return user.has_perm('reports.generate_reports')


def user_can_view_all_reports(user):
    """Check if user can view all reports."""
    return user.has_perm('reports.view_all_reports')
