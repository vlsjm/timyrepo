from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required, permission_required
from django.contrib import messages
from django.views.decorators.http import require_http_methods
from django.utils import timezone
from datetime import datetime, timedelta, date
from .models import HourLog
from .forms import HourLogForm
from users.decorators import intern_required, supervisor_or_admin_required


def get_month_dates(month_date=None):
    """Get the start (1st) and end (last day) of a month."""
    if month_date is None:
        month_date = timezone.now().date()
    elif isinstance(month_date, str):
        month_date = datetime.strptime(month_date, '%Y-%m-%d').date()
    
    # Get the first day of the month
    month_start = month_date.replace(day=1)
    
    # Get the last day of the month
    if month_date.month == 12:
        month_end = month_date.replace(year=month_date.year + 1, month=1, day=1) - timedelta(days=1)
    else:
        month_end = month_date.replace(month=month_date.month + 1, day=1) - timedelta(days=1)
    
    return month_start, month_end


@intern_required
def log_hours(request):
    """Create a new hour log entry."""
    if request.method == 'POST':
        form = HourLogForm(request.POST)
        if form.is_valid():
            log = form.save(commit=False)
            log.intern = request.user
            
            # Check for duplicate entry on same date
            if HourLog.objects.filter(intern=request.user, date=log.date).exists():
                messages.error(request, 'You have already logged hours for this date.')
                return redirect('logging_app:log_hours')
            
            log.save()
            messages.success(request, 'Hours logged successfully!')
            return redirect('logging_app:logs')
    else:
        form = HourLogForm(initial={'date': timezone.now().date()})
    
    context = {'form': form}
    return render(request, 'logging_app/log_hours.html', context)


@intern_required
def logs(request):
    """View hour logs organized by month with two tables (1-15, 16-31)."""
    # Get month parameter or default to current month
    month_str = request.GET.get('month', '') or timezone.now().date().replace(day=1).isoformat()
    month_start, month_end = get_month_dates(month_str)
    
    # Get all logs for this month
    all_month_logs = HourLog.objects.filter(
        intern=request.user,
        date__gte=month_start,
        date__lte=month_end
    ).order_by('date')
    
    # Split logs into two tables: 1-15 and 16-31
    first_half_logs = [log for log in all_month_logs if log.date.day <= 15]
    second_half_logs = [log for log in all_month_logs if log.date.day > 15]
    
    # Calculate monthly statistics (all logs, not just approved)
    monthly_hours = sum(log.total_hours() for log in all_month_logs)
    monthly_submitted = sum(log.total_hours() for log in all_month_logs if log.status == 'submitted')
    
    # Get all months with data for navigation
    all_logs = HourLog.objects.filter(intern=request.user)
    if all_logs.exists():
        first_log_date = all_logs.earliest('date').date
        last_log_date = all_logs.latest('date').date
    else:
        first_log_date = timezone.now().date()
        last_log_date = timezone.now().date()
    
    # Generate list of all month starts
    all_months = []
    current_month = last_log_date.replace(day=1)
    first_month = first_log_date.replace(day=1)
    while current_month >= first_month:
        all_months.append(current_month)
        if current_month.month == 1:
            current_month = current_month.replace(year=current_month.year - 1, month=12)
        else:
            current_month = current_month.replace(month=current_month.month - 1)
    
    # Navigation
    if month_start.month == 1:
        prev_month = month_start.replace(year=month_start.year - 1, month=12)
    else:
        prev_month = month_start.replace(month=month_start.month - 1)
    
    if month_start.month == 12:
        next_month = month_start.replace(year=month_start.year + 1, month=1)
    else:
        next_month = month_start.replace(month=month_start.month + 1)
    
    context = {
        'first_half_logs': first_half_logs,
        'second_half_logs': second_half_logs,
        'month_start': month_start,
        'month_end': month_end,
        'monthly_hours': monthly_hours,
        'monthly_submitted': monthly_submitted,
        'prev_month': prev_month.isoformat(),
        'next_month': next_month.isoformat(),
        'all_months': all_months,
        'current_month': month_start,
    }
    return render(request, 'logging_app/logs.html', context)


@intern_required
def edit_log(request, pk):
    """Edit an hour log entry. Interns can only edit their own logs."""
    log = get_object_or_404(HourLog, pk=pk, intern=request.user)
    
    if not log.is_editable():
        messages.error(request, 'You can only edit draft logs.')
        return redirect('logging_app:logs')
    
    if request.method == 'POST':
        form = HourLogForm(request.POST, instance=log)
        if form.is_valid():
            form.save()
            messages.success(request, 'Log updated successfully!')
            return redirect('logging_app:logs')
    else:
        form = HourLogForm(instance=log)
    
    context = {
        'form': form,
        'log': log,
        'is_edit': True,
    }
    return render(request, 'logging_app/log_hours.html', context)


@intern_required
@require_http_methods(['POST'])
def delete_log(request, pk):
    """Delete an hour log entry. Interns can only delete their own draft logs."""
    log = get_object_or_404(HourLog, pk=pk, intern=request.user)
    
    if not log.is_editable():
        messages.error(request, 'You can only delete draft logs.')
        return redirect('logging_app:logs')
    
    log.delete()
    messages.success(request, 'Log deleted successfully!')
    return redirect('logging_app:logs')


@login_required
def log_detail(request, pk):
    """View details of a single log entry."""
    log = get_object_or_404(HourLog, pk=pk)
    
    # Check permissions
    if log.intern != request.user and not request.user.is_supervisor():
        if not request.user.is_admin():
            messages.error(request, 'You do not have permission to view this log.')
            return redirect('dashboard')
    
    context = {'log': log}
    return render(request, 'logging_app/log_detail.html', context)
