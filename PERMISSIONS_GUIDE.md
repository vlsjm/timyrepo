# Django Groups & Permissions System

## Overview

The Internship Hours Tracker now uses **Django's Groups and Permissions** system for role-based access control. This provides a scalable, flexible approach to managing user access.

## Groups

Three main groups are established:

### 1. **Intern**
- Can log hours (`log_hours`)
- Can view own logs (`view_own_logs`)
- Can edit own logs (`edit_own_logs`)
- Can delete own logs (`delete_own_logs`)
- Can submit logs for review (`submit_for_review`)
- Can generate reports (`generate_reports`)

### 2. **Supervisor**
- Can view all logs (`view_all_logs`)
- Can approve hour logs (`approve_logs`)
- Can reject hour logs (`reject_logs`)

### 3. **Admin**
- Has **all permissions** from all groups
- Full system access

## Permissions

Each permission is associated with the `HourLog` model and has a clear codename:

```
- log_hours              → Can log hours
- view_own_logs          → Can view own logs
- edit_own_logs          → Can edit own logs
- delete_own_logs        → Can delete own logs
- submit_for_review      → Can submit logs for review
- view_all_logs          → Can view all hour logs
- approve_logs           → Can approve hour logs
- reject_logs            → Can reject hour logs
- generate_reports       → Can generate reports
```

## Setup

### Initialize Groups and Permissions

Run this management command to set up all groups and permissions:

```bash
python manage.py setup_groups
```

This will:
1. Create three groups: Intern, Supervisor, Admin
2. Create all custom permissions
3. Assign appropriate permissions to each group

**Output:**
```
[CHECK] Groups and permissions created successfully
   Intern group: 6 permissions
   Supervisor group: 3 permissions
   Admin group: 40+ permissions
```

## Automatic Group Assignment

When a user is created or their role changes:

1. **Role Field + Groups Sync**: The `CustomUser.save()` method automatically assigns the user to the corresponding group based on their role
2. **Profile Creation**: Signals automatically create the appropriate profile (InternProfile, SupervisorProfile, AdminProfile)

**Example:**
```python
# Creating a new user via admin or registration
user = CustomUser.objects.create_user(
    email='intern@example.com',
    password='secure123',
    role='intern'  # Automatically added to "Intern" group
)

# Changing a user's role
user.role = 'supervisor'
user.save()  # Automatically moved to "Supervisor" group
```

## Usage in Views

### 1. Using Group Decorators

```python
from users.decorators import intern_required, supervisor_or_admin_required

@intern_required
def log_hours(request):
    # Only interns can access
    ...

@supervisor_or_admin_required
def approve_logs(request):
    # Only supervisors and admins can access
    ...
```

### 2. Using Permission Functions

```python
from users.permissions import has_permission, is_intern

def my_view(request):
    if has_permission(request.user, 'log_hours'):
        # User can log hours
        ...
    
    if is_intern(request.user):
        # User is an intern
        ...
```

### 3. In Templates

```html
{% if user.is_authenticated %}
    {% if user.groups.all|intersect:"Intern" %}
        <a href="{% url 'logging_app:log_hours' %}">Log Hours</a>
    {% endif %}
    
    {% if user.has_perm 'logging_app.approve_logs' %}
        <a href="/approve/">Approve Logs</a>
    {% endif %}
{% endif %}
```

## Permission Utility Functions

### Import from `users.permissions`:

```python
from users.permissions import (
    has_permission,           # Check single permission
    has_any_permission,       # Check if user has any permission
    has_all_permissions,      # Check if user has all permissions
    is_intern,               # Check if user is intern
    is_supervisor,           # Check if user is supervisor
    is_admin,                # Check if user is admin
)
```

### Examples:

```python
# Check single permission
if has_permission(request.user, 'log_hours'):
    # Allow action

# Check multiple permissions
if has_any_permission(request.user, ['approve_logs', 'reject_logs']):
    # User can review logs

if has_all_permissions(request.user, ['view_all_logs', 'approve_logs']):
    # User is a full supervisor
```

## Decorator Options

### Basic Decorators (No Arguments)

```python
@intern_required
def intern_only_view(request):
    ...

@supervisor_or_admin_required
def supervisor_view(request):
    ...
```

### With Custom Redirect URL

```python
@intern_required(redirect_url='dashboard')
def log_hours(request):
    ...

@supervisor_required(redirect_url='users:login')
def approve_logs(request):
    ...
```

## Admin Panel

All groups and permissions are visible in the Django admin at `/admin/`:

1. **Auth > Groups** - View and manage groups
2. **Auth > Permissions** - View all permissions
3. **Users > Users** - Assign users to groups, modify roles

## Migration Guide

If upgrading from the old role-based system:

1. **Backward Compatible**: The old `is_intern()`, `is_supervisor()`, `is_admin()` methods still work
2. **New System**: Permissions are now stored in Django's `Permission` model
3. **Both Work**: Role field AND group membership are synced and maintained

### Old Way (Still Works)

```python
if request.user.is_intern():
    # Access granted
```

### New Way (Recommended)

```python
if has_permission(request.user, 'log_hours'):
    # Access granted
```

## Custom Permissions

To add a new permission:

1. **Add to management command** (`users/management/commands/setup_groups.py`)
2. **Add to permissions tuple** in the command
3. **Run**: `python manage.py setup_groups`

Example:
```python
# In setup_groups.py
permissions_map = {
    'log_hours': 'Can log hours',
    'view_own_logs': 'Can view own logs',
    'my_custom_permission': 'Can do something custom',  # Add here
}
```

## Implementation Checklist

- [CHECK] Groups system implemented
- [CHECK] Permissions assigned to groups
- [CHECK] Automatic group assignment on user save
- [CHECK] Decorators updated with group-based checks
- [CHECK] Permission utility functions created
- [CHECK] Management command for setup
- [CHECK] Backward compatible with old role system

## Troubleshooting

### Groups not created?

```bash
python manage.py setup_groups
```

### User not in correct group?

Check in admin:
1. Go to `/admin/auth/user/`
2. Click user
3. Verify "Groups" field shows correct group
4. Check "Role" field matches

### Permission denied errors?

1. **Check group membership**: `user.groups.all()`
2. **Check specific permission**: `user.has_perm('logging_app.permission_name')`
3. **Run setup command**: `python manage.py setup_groups`

## Security Notes

- Superusers (staff) have all permissions by default
- Always use `@login_required` before role-based decorators
- Check permissions in views AND templates (defense in depth)
- Use Django's built-in `@permission_required` decorator for fine-grained control

---

**For questions or issues**, check the Django documentation on [Groups and Permissions](https://docs.djangoproject.com/en/4.2/topics/auth/default/#permissions-and-authorization)
