"""
Utility decorators and helpers for role-based access control.
Uses Django groups and permissions system for flexible access management.
"""
from functools import wraps
from django.contrib import messages
from django.shortcuts import redirect
from django.core.exceptions import PermissionDenied
from .permissions import is_intern, is_supervisor, is_admin, has_permission, has_any_permission


def intern_required(view_func=None, redirect_url='dashboard'):
    """Decorator to restrict access to interns only."""
    def decorator(func):
        @wraps(func)
        def wrapped_view(request, *args, **kwargs):
            if not request.user.is_authenticated:
                messages.error(request, 'Please log in first.')
                return redirect('users:login')
            
            if not is_intern(request.user):
                messages.error(request, 'Only interns can access this page.')
                return redirect(redirect_url)
            
            return func(request, *args, **kwargs)
        return wrapped_view
    
    # Support both @intern_required and @intern_required() syntax
    if view_func is not None:
        return decorator(view_func)
    return decorator


def supervisor_required(view_func=None, redirect_url='dashboard'):
    """Decorator to restrict access to supervisors only."""
    def decorator(func):
        @wraps(func)
        def wrapped_view(request, *args, **kwargs):
            if not request.user.is_authenticated:
                messages.error(request, 'Please log in first.')
                return redirect('users:login')
            
            if not is_supervisor(request.user):
                messages.error(request, 'Only supervisors can access this page.')
                return redirect(redirect_url)
            
            return func(request, *args, **kwargs)
        return wrapped_view
    
    if view_func is not None:
        return decorator(view_func)
    return decorator


def admin_required(view_func=None, redirect_url='dashboard'):
    """Decorator to restrict access to admins only."""
    def decorator(func):
        @wraps(func)
        def wrapped_view(request, *args, **kwargs):
            if not request.user.is_authenticated:
                messages.error(request, 'Please log in first.')
                return redirect('users:login')
            
            if not is_admin(request.user):
                messages.error(request, 'Only administrators can access this page.')
                return redirect(redirect_url)
            
            return func(request, *args, **kwargs)
        return wrapped_view
    
    if view_func is not None:
        return decorator(view_func)
    return decorator


def supervisor_or_admin_required(view_func=None, redirect_url='dashboard'):
    """Decorator to restrict access to supervisors and admins."""
    def decorator(func):
        @wraps(func)
        def wrapped_view(request, *args, **kwargs):
            if not request.user.is_authenticated:
                messages.error(request, 'Please log in first.')
                return redirect('users:login')
            
            if not (is_supervisor(request.user) or is_admin(request.user)):
                messages.error(request, 'Only supervisors and administrators can access this page.')
                return redirect(redirect_url)
            
            return func(request, *args, **kwargs)
        return wrapped_view
    
    if view_func is not None:
        return decorator(view_func)
    return decorator


def permission_required_custom(permission_codename, redirect_url='dashboard'):
    """
    Decorator to check custom permissions.
    Uses Django's permission system.
    
    Usage:
        @permission_required_custom('log_hours')
        def log_hours(request):
            ...
    """
    def decorator(view_func):
        @wraps(view_func)
        def wrapped_view(request, *args, **kwargs):
            if not request.user.is_authenticated:
                messages.error(request, 'Please log in first.')
                return redirect('users:login')
            
            if not has_permission(request.user, permission_codename):
                messages.error(request, 'You do not have permission to access this page.')
                return redirect(redirect_url)
            
            return view_func(request, *args, **kwargs)
        return wrapped_view
    return decorator


def any_permission_required(permission_codenames, redirect_url='dashboard'):
    """
    Decorator to check if user has any of the specified permissions.
    
    Usage:
        @any_permission_required(['approve_logs', 'reject_logs'])
        def review_logs(request):
            ...
    """
    def decorator(view_func):
        @wraps(view_func)
        def wrapped_view(request, *args, **kwargs):
            if not request.user.is_authenticated:
                messages.error(request, 'Please log in first.')
                return redirect('users:login')
            
            if not has_any_permission(request.user, permission_codenames):
                messages.error(request, 'You do not have permission to access this page.')
                return redirect(redirect_url)
            
            return view_func(request, *args, **kwargs)
        return wrapped_view
    return decorator
