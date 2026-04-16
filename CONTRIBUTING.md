# Contributing Guidelines

Welcome to the Internship Hours Tracker project! This document outlines the standards and best practices we follow to maintain code quality, consistency, and readability.

## Table of Contents

1. [Code Style](#code-style)
2. [CSS Guidelines](#css-guidelines)
3. [Python Standards](#python-standards)
4. [Django Conventions](#django-conventions)
5. [Template Rules](#template-rules)
6. [Commit Messages](#commit-messages)
7. [Development Workflow](#development-workflow)
8. [Testing](#testing)
9. [Documentation](#documentation)

---

## Code Style

### General Rules

- Use consistent indentation (2 spaces for HTML/CSS, 4 spaces for Python)
- Keep lines under 100 characters where possible
- Use UTF-8 encoding for all files
- Include appropriate file headers/docstrings

### Tools

- **Python Formatting**: Black (`pip install black`)
- **Linting**: Flake8 (`pip install flake8`)
- **Code Quality**: Type hints for functions (Python 3.8+)

**Format on save:**
```bash
black .
flake8 .
```

---

## CSS Guidelines

### [CHECK] **DO**

- [CHECK] Use **external CSS files** in `static/css/`
- [CHECK] Use **Tailwind CSS classes** in templates
- [CHECK] Keep responsive design in mind (mobile-first approach)
- [CHECK] Use semantic class names (`btn-primary`, `card-header`, etc.)
- [CHECK] Group related styles together

**Good Example:**
```html
<!-- In template -->
<div class="bg-white rounded-lg shadow p-6">
    <h1 class="text-2xl font-bold text-gray-900">Title</h1>
</div>
```

### [X] **DON'T**

- [X] **NEVER** use inline `style=""` attributes
- [X] **NEVER** add custom CSS in templates
- [X] **NEVER** use `!important` flags
- [X] **NEVER** use deprecated HTML attributes like `bgcolor`, `cellpadding`

**Bad Example (Don't do this):**
```html
<!-- [X] WRONG -->
<div style="background: white; padding: 20px; border-radius: 8px;">
    <h1 style="font-size: 24px; font-weight: bold;">Title</h1>
</div>
```

### Mobile-First Design

All templates must be mobile-responsive using Tailwind's breakpoint system:

```html
<!-- Mobile first (default), then tablet/desktop -->
<div class="w-full md:w-1/2 lg:w-1/3">
    Content
</div>
```

**Breakpoints:**
- `sm`: 640px
- `md`: 768px
- `lg`: 1024px
- `xl`: 1280px

---

## Python Standards

### Code Style

Follow **PEP 8** with these specifics:

```python
# [CHECK] Good
def calculate_hours(time_in, time_out):
    """Calculate total hours between two times."""
    delta = time_out - time_in
    hours = delta.total_seconds() / 3600
    return round(hours, 2)


# [X] Avoid
def calc_h(t1,t2):
    s=(t2-t1).total_seconds()
    return s/3600
```

### Type Hints

Use type hints for all new functions:

```python
# [CHECK] Good
def has_permission(user: CustomUser, permission: str) -> bool:
    return user.has_perm(f'logging_app.{permission}')

# [X] Avoid
def has_permission(user, permission):
    return user.has_perm(f'logging_app.{permission}')
```

### Docstrings

All functions, classes, and modules should have docstrings:

```python
def log_hours(request):
    """
    Create a new hour log entry.
    
    Args:
        request: HTTP request object
    
    Returns:
        HttpResponse: Rendered form or redirect on success
    
    Raises:
        ValidationError: If duplicate entry exists for date
    """
    ...
```

### Line Length

- **Maximum**: 100 characters
- Use Black for automatic formatting

```bash
black --line-length 100 .
```

### Imports

Group imports in this order:

```python
# 1. Standard library
import os
from datetime import datetime

# 2. Third-party
from django.db import models

# 3. Local imports
from users.models import CustomUser
from .permissions import has_permission
```

---

## Django Conventions

### Models

- Always use descriptive field names
- Include `verbose_name` and `verbose_name_plural` in Meta
- Add docstrings explaining the model's purpose

```python
class HourLog(models.Model):
    """
    Model for logging daily work hours.
    Each entry represents a day's work with time in/out and description.
    """
    
    intern = models.ForeignKey(User, on_delete=models.CASCADE)
    date = models.DateField()
    time_in = models.TimeField()
    time_out = models.TimeField()
    
    class Meta:
        verbose_name = 'Hour Log'
        verbose_name_plural = 'Hour Logs'
        ordering = ['-date']
    
    def __str__(self):
        return f"{self.intern.get_full_name()} - {self.date}"
```

### Views

- Always use `@login_required` decorator
- Use permission/group decorators from `users.decorators`
- Keep views focused (thin controllers pattern)
- Return appropriate HTTP status codes

```python
from django.contrib.auth.decorators import login_required
from users.decorators import intern_required

@intern_required
def log_hours(request):
    """Create a new hour log entry."""
    if request.method == 'POST':
        form = HourLogForm(request.POST)
        if form.is_valid():
            # Process
            return redirect('logging_app:logs')
    else:
        form = HourLogForm()
    
    return render(request, 'logging_app/log_hours.html', {'form': form})
```

### Forms

- Validate all user input
- Use Django's built-in form widgets
- Add helpful error messages
- Include placeholders on input fields

```python
class HourLogForm(forms.ModelForm):
    class Meta:
        model = HourLog
        fields = ('date', 'time_in', 'time_out', 'description')
        widgets = {
            'date': forms.DateInput(attrs={
                'type': 'date',
                'class': 'form-control',
                'placeholder': 'Choose date'
            }),
        }
```

### URLs

- Use descriptive URL patterns
- Always use `app_name` in app-level urls.py
- Use `path()` instead of `re_path()` when possible

```python
# users/urls.py
app_name = 'users'

urlpatterns = [
    path('', views.index, name='index'),
    path('register/', views.register, name='register'),
    path('login/', views.login_view, name='login'),
]
```

### Admin Configuration

- Always register models in admin
- Use `list_display`, `list_filter`, `search_fields`
- Make read-only fields properly marked

```python
@admin.register(HourLog)
class HourLogAdmin(admin.ModelAdmin):
    list_display = ('intern', 'date', 'total_hours', 'status')
    list_filter = ('status', 'date')
    search_fields = ('intern__email', 'description')
    readonly_fields = ('created_at', 'updated_at')
```

---

## Template Rules

### File Organization

```
templates/
├── base.html              # Base template with navigation
├── dashboard.html         # Main dashboard
├── users/
│   ├── index.html
│   ├── login.html
│   ├── register.html
│   └── profile.html
├── logging_app/
│   ├── log_hours.html
│   ├── logs.html
│   └── log_detail.html
└── reports/
    ├── dashboard.html
    ├── generate_journal.html
    ├── generate_timesheet.html
    ├── timesheet_view.html
    └── view_report.html
```

### Best Practices

[CHECK] **DO:**
- Use template inheritance (`{% extends "base.html" %}`)
- Use `{% url %}` tag for all links
- Use `{% load %}` for custom template tags
- Block out sections with `{% block %}`
- Use descriptive block names

[CHECK] **SECURITY:**
- Always escape variables: `{{ variable }}`
- Use `{% csrf_token %}` in all forms
- Use `{% if user.is_authenticated %}`
- Check permissions in templates too

[X] **DON'T:**
- Never hardcode URLs (`/admin/` → use `{% url 'admin:index' %}`)
- Never put logic in templates
- Never use `|safe` filter without review
- Never put CSS/JS in templates

### Template Example

```html
{% extends "base.html" %}

{% block title %}Page Title{% endblock %}

{% block content %}
<div class="container mx-auto px-4">
    {% if messages %}
        {% for message in messages %}
        <div class="alert alert-{{ message.tags }}">
            {{ message }}
        </div>
        {% endfor %}
    {% endif %}

    {% if user.is_authenticated %}
        <h1>Welcome, {{ user.first_name }}!</h1>
    {% else %}
        <p><a href="{% url 'users:login' %}">Log in</a></p>
    {% endif %}
</div>
{% endblock %}
```

---

## Commit Messages

Follow the conventional commits format:

### Format

```
<type>(<scope>): <subject>

<body>

<footer>
```

### Types

- `feat`: A new feature
- `fix`: A bug fix
- `docs`: Documentation changes
- `style`: Code style changes (formatting, semicolons, etc.)
- `refactor`: Code refactoring
- `test`: Adding or updating tests
- `chore`: Dependency updates, configs

### Examples

```
feat(logging): Add ability to submit logs for supervisor review

- Add submit_log view
- Add permission check for supervisors
- Update HourLog model with reviewed_by field

Closes #42

---

fix(dashboard): Fix progress percentage calculation

Calculate based on completed hours only, not submitted hours.

---

docs(readme): Update installation instructions

---

refactor(permissions): Replace role-based checks with Django groups

Use has_permission() utility instead of is_intern() checks.
```

---

## Development Workflow

### 1. Setup Environment

```bash
# Create virtual environment
python -m venv .venv

# Activate
.venv\Scripts\Activate.ps1  # Windows
source .venv/bin/activate    # macOS/Linux

# Install dependencies
pip install -r requirements.txt

# Setup groups and permissions
python manage.py migrate
python manage.py setup_groups
```

### 2. Create a Feature

```bash
# Create a new branch
git checkout -b feat/feature-name

# Make changes, test, commit
git add .
git commit -m "feat(app): Description of feature"

# Push and create PR
git push origin feat/feature-name
```

### 3. Before Committing

```bash
# Format code
black .

# Check for style issues
flake8 .

# Run tests (when available)
python manage.py test

# Check for migrations
python manage.py makemigrations --check
```

### 4. Pull Request Checklist

- [ ] Code is formatted with Black
- [ ] No flake8 warnings
- [ ] New migrations created if needed
- [ ] Tests pass (if applicable)
- [ ] Documentation updated
- [ ] Commit messages are descriptive
- [ ] No console.log() or print() statements (except for errors)

---

## Testing

### Running Tests

```bash
# Run all tests
python manage.py test

# Run specific app tests
python manage.py test users

# Run with verbosity
python manage.py test -v 2

# Run with coverage
coverage run --source='.' manage.py test
coverage report
```

### Writing Tests

Place tests in `<app>/tests/`:

```python
# logging_app/tests/test_models.py
from django.test import TestCase
from logging_app.models import HourLog


class HourLogTestCase(TestCase):
    def setUp(self):
        """Create test data."""
        self.log = HourLog.objects.create(...)
    
    def test_total_hours_calculation(self):
        """Test that hours are calculated correctly."""
        self.assertEqual(self.log.total_hours(), 8.0)
    
    def test_cannot_create_duplicate_date(self):
        """Test that duplicate entries on same date are prevented."""
        with self.assertRaises(ValidationError):
            HourLog.objects.create(...)
```

### Code Coverage Goals

- **Minimum**: 70% coverage
- **Target**: 85%+ coverage
- **Focus areas**: Models, utilities, permissions

---

## Documentation

### README

- Project description
- Quick start guide
- Feature list
- Installation steps
- Usage examples

### Docstrings

Every module, class, and function should have:

```python
"""
One-line summary.

Longer description if needed. Explain the purpose, behavior, and any
important details.

Args:
    param1: Description of param1
    param2: Description of param2

Returns:
    Description of return value

Raises:
    ExceptionType: When this exception is raised

Example:
    >>> result = function(param1, param2)
    >>> print(result)
"""
```

### Inline Comments

Use sparingly. Code should be self-documenting:

```python
# [X] Unnecessary
total = 0  # Initialize total to zero

# [CHECK] Valuable
# Exclude rejected logs from total hours
total = sum(log.total_hours() for log in logs if log.status != 'rejected')
```

---

## Code Review Checklist

When reviewing code, ensure:

- [CHECK] No inline CSS/styles
- [CHECK] Type hints present
- [CHECK] Docstrings are complete
- [CHECK] Permission checks included
- [CHECK] Error handling is appropriate
- [CHECK] Database queries are optimized
- [CHECK] No hardcoded URLs
- [CHECK] Tests pass
- [CHECK] Commit message is descriptive
- [CHECK] No sensitive data in code

---

## Project Structure

```
internshiptracker/
├── config/                    # Project settings
├── users/                     # User management app
├── logging_app/               # Hour logging app
├── reports/                   # Reports app
├── templates/                 # Django templates
├── static/                    # CSS, JS, images
│   ├── css/                  # [CHECK] CSS goes here
│   ├── js/                   # JavaScript files
│   └── images/
├── .venv/                    # Virtual environment
├── manage.py
├── requirements.txt
├── .editorconfig
├── .pre-commit-config.yaml
├── CONTRIBUTING.md           # This file
├── PERMISSIONS_GUIDE.md      # Permission system docs
└── README.md
```

---

## Getting Help

- **Documentation**: See [PERMISSIONS_GUIDE.md](PERMISSIONS_GUIDE.md) for permission system
- **Django Docs**: https://docs.djangoproject.com/
- **Python PEP 8**: https://pep8.org/
- **Tailwind CSS**: https://tailwindcss.com/docs

---

## Code of Conduct

- Be respectful and constructive in code reviews
- Ask questions if code is unclear
- Assume good intentions
- Help others learn and improve

---

**Last Updated**: April 2026

**Version**: 1.0

**Questions?** Open an issue in the repository.
