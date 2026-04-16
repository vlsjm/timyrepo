# Permission & Access Control System

This document describes the refactored role-based access control system using Django groups and permissions.

## Overview

The system now uses **Django Groups and Permissions** for role-based access control, providing:
- [CHECK] Fine-grained permission management
- [CHECK] Scalable access control
- [CHECK] Follows Django best practices
- [CHECK] Integration with Django admin

## Setup

### 1. Run the Setup Command

After migrations, initialize groups and permissions:

```bash
python manage.py setup_groups_permissions
```

This creates:
- **3 Groups**: Intern, Supervisor, Admin
- **11 Permissions**: Specific operations for different roles
- **Group assignments**: Links groups to permissions

### 2. Verify Setup

```bash
python manage.py shell
>>> from django.contrib.auth.models import Group
>>> for group in Group.objects.all():
...     print(f"{group.name}: {group.permissions.count()} permissions")
```

## User Roles & Permissions

### 👤 INTERN
**Permissions:**
- `log_hours` - Can log daily work hours
- `view_own_logs` - Can view own hour logs
- `edit_own_logs` - Can edit own draft logs
- `delete_own_logs` - Can delete own draft logs
- `submit_logs` - Can submit logs for review
- `generate_reports` - Can generate reports
- `view_own_reports` - Can view own reports

### [USERS] SUPERVISOR
**Permissions:**
- `view_all_logs` - Can view all interns' logs
- `approve_logs` - Can approve submitted logs
- `reject_logs` - Can reject submitted logs
- `view_all_reports` - Can view all reports

### [SETTINGS] ADMIN (Superuser equivalent)
**Permissions:** All of the above + Django admin access

## Using Access Controls

### 1. Using Decorators (Recommended)

```python
from users.decorators import (
    intern_required,
    supervisor_required,
    admin_required,
    supervisor_or_admin_required
)

@intern_required
def log_hours(request):
    # Only interns can access
    pass

@supervisor_or_admin_required
def approve_logs(request):
    # Only supervisors and admins can access
    pass
```

### 2. Using Permission Decorators

```python
from django.contrib.auth.decorators import permission_required

@permission_required('logging_app.log_hours')
def log_hours(request):
    # Only users with log_hours permission
    pass

@permission_required(['logging_app.approve_logs', 'logging_app.view_all_logs'])
def approve_logs(request):
    # User must have both permissions
    pass
```

### 3. In Templates

```django
{% if perms.logging_app.log_hours %}
    <a href="{% url 'logging_app:log_hours' %}">Log Hours</a>
{% endif %}

{% if perms.logging_app.approve_logs %}
    <button>Approve Log</button>
{% endif %}
```

### 4. In Views (Manual Checks)

```python
from users.permissions import (
    user_can_log_hours,
    user_can_approve_logs,
    user_can_view_all_logs
)

def some_view(request):
    if user_can_approve_logs(request.user):
        # Show approval options
        pass
    
    if user_can_view_all_logs(request.user):
        logs = HourLog.objects.all()
    else:
        logs = HourLog.objects.filter(intern=request.user)
```

## Automatic Group Assignment

When a user's role is changed:
1. User is removed from all groups
2. User is automatically added to the correct group based on their role
3. All permissions are automatically updated

**Example:**
```python
user.role = 'supervisor'
user.save()  # Automatically assigned to Supervisor group
```

## Admin Panel

### Creating Users

1. Go to `/admin/users/customuser/`
2. Click "Add Custom User"
3. Fill in email, password, first/last name
4. Select a **Role** (Intern, Supervisor, Admin)
5. Save

The user is automatically assigned to the correct group!

### Assigning Permissions Manually

To give a user additional permissions without changing their role:

1. Go to `/admin/auth/user/`
2. Select a user
3. In the "Groups" section, add groups or individual permissions
4. Save

## Migration from Old System

The old `is_intern()`, `is_supervisor()`, `is_admin()` methods are still available and work properly:

```python
# Old way (still works)
if request.user.is_intern():
    pass

# New way (preferred)
if request.user.has_perm('logging_app.log_hours'):
    pass
```

Both approaches work together seamlessly!

## Troubleshooting

### "Groups haven't been created yet"

If you get an error about missing groups, run:
```bash
python manage.py setup_groups_permissions
```

### User not getting permissions after role change

Permissions are assigned via a signal. Make sure:
1. User is saved (not just role changed in memory)
2. Groups exist in database (run setup command)

### Adding Custom Permissions

To add new permissions, update the management command:

1. Edit `users/management/commands/setup_groups_permissions.py`
2. Add to `permissions_to_create` list
3. Run: `python manage.py setup_groups_permissions`

## References

- [Django Permissions Documentation](https://docs.djangoproject.com/en/stable/topics/auth/default/#permissions-and-authorization)
- [Django Groups](https://docs.djangoproject.com/en/stable/topics/auth/default/#groups)
- [Custom User Model](https://docs.djangoproject.com/en/stable/topics/auth/customizing/#using-a-custom-user-model)
