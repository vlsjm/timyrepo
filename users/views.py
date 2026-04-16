from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from django.views.decorators.http import require_http_methods
from django.contrib import messages
from django.utils.decorators import method_decorator
from django.utils import timezone
from django.views.generic import View
from django.forms import modelformset_factory
from .models import CustomUser, InternProfile, SupervisorProfile, AdminProfile, DaySchedule
from .forms import CustomUserCreationForm, InternProfileForm, DayScheduleForm
from .permissions import is_intern, is_supervisor, is_admin
from logging_app.models import HourLog
from datetime import datetime, timedelta
import pytz


def index(request):
    """Landing page."""
    if request.user.is_authenticated:
        return redirect('dashboard')
    return render(request, 'users/index.html')


@require_http_methods(['GET', 'POST'])
def register(request):
    """User registration page."""
    if request.user.is_authenticated:
        return redirect('dashboard')
    
    if request.method == 'POST':
        form = CustomUserCreationForm(request.POST)
        if form.is_valid():
            user = form.save(commit=False)
            user.username = user.email
            user.save()
            
            # Profile is automatically created by post_save signal based on role
            
            return redirect('users:register_success')
    else:
        form = CustomUserCreationForm()
    
    return render(request, 'users/register.html', {'form': form})


def register_success(request):
    """Show registration success popup and redirect to login."""
    return render(request, 'users/register_success.html')


@require_http_methods(['GET', 'POST'])
def login_view(request):
    """User login page."""
    if request.user.is_authenticated:
        return redirect('dashboard')
    
    if request.method == 'POST':
        email = request.POST.get('email')
        password = request.POST.get('password')
        
        try:
            user = CustomUser.objects.get(email=email)
            user = authenticate(request, username=user.username, password=password)
            
            if user is not None:
                login(request, user)
                messages.success(request, f'Welcome back, {user.first_name}!')
                # Handle next parameter for redirects
                next_url = request.GET.get('next')
                if next_url:
                    return redirect(next_url)
                return redirect('dashboard')
            else:
                messages.error(request, 'Invalid email or password.')
        except CustomUser.DoesNotExist:
            messages.error(request, 'Invalid email or password.')
    
    return render(request, 'users/login.html')


@login_required
def logout_view(request):
    """User logout."""
    logout(request)
    messages.success(request, 'You have been logged out.')
    return redirect('users:index')


@login_required
def dashboard(request):
    """Main dashboard - different content based on user role."""
    # Get current time in Philippines timezone (Asia/Manila)
    ph_tz = pytz.timezone('Asia/Manila')
    current_time_ph = timezone.now().astimezone(ph_tz)
    current_hour = current_time_ph.hour
    
    # Calculate time-based greeting
    if current_hour < 12:
        greeting = "Good morning!"
    elif current_hour < 17:
        greeting = "Good afternoon!"
    else:
        greeting = "Good evening!"
    
    context = {
        'user': request.user,
        'greeting': greeting,
    }
    
    if is_intern(request.user):
        try:
            profile = request.user.intern_profile
            context['profile'] = profile
            completed = profile.completed_hours()
            required = profile.required_hours
            context['completed_hours'] = completed
            context['remaining_hours'] = profile.remaining_hours()
            progress_pct = profile.progress_percentage()
            context['progress_percentage'] = progress_pct
            # Calculate stroke-dasharray for SVG circular progress (circumference = 2πr = 2π(45) ≈ 282.7)
            # We need to show the arc proportional to progress_percentage
            context['stroke_dasharray'] = round((progress_pct / 100.0) * 282.7, 1) if progress_pct > 0 else 0
            
            # Get recent logs
            recent_logs = HourLog.objects.filter(intern=request.user).order_by('-date')[:5]
            context['recent_logs'] = recent_logs
            
            # Weekly summary
            today = timezone.now().date()
            week_start = today - timedelta(days=today.weekday())
            week_logs = HourLog.objects.filter(
                intern=request.user,
                date__gte=week_start
            )
            context['weekly_hours'] = sum(log.total_hours() for log in week_logs)
            
            # NEW: Days remaining until internship end date
            if profile.end_date:
                days_remaining = (profile.end_date - today).days
                context['days_remaining'] = days_remaining
                context['is_overdue'] = days_remaining < 0
                context['days_overdue'] = abs(days_remaining) if days_remaining < 0 else 0
                context['end_date_formatted'] = profile.end_date.strftime('%B %d, %Y')
                
                # Calculate working days remaining based on schedule
                working_days_remaining = 0
                day_names_map = {0: 'monday', 1: 'tuesday', 2: 'wednesday', 3: 'thursday', 4: 'friday', 5: 'saturday', 6: 'sunday'}
                for i in range(days_remaining + 1):  # Include today
                    future_date = today + timedelta(days=i)
                    day_of_week = day_names_map[future_date.weekday()]
                    try:
                        day_schedule = DaySchedule.objects.get(user=request.user, day_of_week=day_of_week)
                        if day_schedule.is_working_day:
                            working_days_remaining += 1
                    except DaySchedule.DoesNotExist:
                        pass
                context['working_days_remaining'] = working_days_remaining
            else:
                context['days_remaining'] = None
                context['is_overdue'] = False
                context['days_overdue'] = 0
                context['end_date_formatted'] = None
                context['working_days_remaining'] = None
            
            # NEW: Weekly breakdown - hours per day for current week (Mon-Sun)
            weekly_breakdown = {}
            for i in range(7):
                day_date = week_start + timedelta(days=i)
                day_logs = week_logs.filter(date=day_date)
                hours = sum(log.total_hours() for log in day_logs)
                day_name = day_date.strftime('%a')
                weekly_breakdown[day_name] = hours
            context['weekly_breakdown'] = weekly_breakdown
            

            # NEW: Total unique logged days (logging streak = count of unique dates with logs)
            all_logs = HourLog.objects.filter(intern=request.user)
            unique_logged_dates = all_logs.values_list('date', flat=True).distinct().count()
            context['total_unique_logged_days'] = unique_logged_dates
            
            # NEW: Smart Metrics - Average hours/day, pace tracking, alerts
            # Calculate average hours per day logged
            if unique_logged_dates > 0:
                avg_hours_per_day = completed / unique_logged_dates
            else:
                avg_hours_per_day = 0
            context['avg_hours_per_day'] = round(avg_hours_per_day, 1)
            
            # Calculate required pace (hours per day needed to finish on time)
            if profile.start_date and profile.end_date:
                total_days = (profile.end_date - profile.start_date).days + 1
                required_pace = required / total_days if total_days > 0 else 0
                context['required_pace'] = round(required_pace, 1)
                
                # Calculate current pace (average hours per calendar day from start to today)
                days_elapsed = (today - profile.start_date).days + 1
                current_pace = completed / days_elapsed if days_elapsed > 0 else 0
                context['current_pace'] = round(current_pace, 1)
            else:
                context['required_pace'] = 0
                context['current_pace'] = 0
            
            # Determine alert status
            if context['days_remaining'] is not None:
                if context['is_overdue']:
                    context['alert_status'] = 'overdue'
                    context['alert_message'] = f"Internship ended {context['days_overdue']} days ago"
                elif context['days_remaining'] <= 0:
                    context['alert_status'] = 'overdue'
                    context['alert_message'] = "Internship has ended"
                elif context['working_days_remaining'] < 5:
                    if progress_pct < (100 * (context['required_pace'] / required)) if required > 0 else False:
                        context['alert_status'] = 'behind'
                        context['alert_message'] = f"Behind schedule with {context['working_days_remaining']} working days remaining"
                    else:
                        context['alert_status'] = 'on-track'
                        context['alert_message'] = f"On track with {context['working_days_remaining']} working days to go"
                elif progress_pct >= 100:
                    context['alert_status'] = 'ahead'
                    context['alert_message'] = "Goal reached! Excellent progress"
                elif context['current_pace'] < context['required_pace']:
                    context['alert_status'] = 'behind'
                    context['alert_message'] = f"Pace needs improvement. Required {context['required_pace']} hrs/day, currently {context['current_pace']} hrs/day"
                else:
                    context['alert_status'] = 'on-track'
                    context['alert_message'] = "On track. Keep up the consistency"
            else:
                context['alert_status'] = 'info'
                context['alert_message'] = "Set your internship end date to track progress"
            
            # Days since last log
            if all_logs.exists():
                last_log_date = all_logs.first().date
                days_since_last_log = (today - last_log_date).days
                context['days_since_last_log'] = days_since_last_log
            else:
                context['days_since_last_log'] = None
            
        except InternProfile.DoesNotExist:
            # Provide default values if profile doesn't exist
            context['profile'] = None
            context['completed_hours'] = 0
            context['remaining_hours'] = 0
            context['progress_percentage'] = 0
            context['stroke_dasharray'] = 0
            context['recent_logs'] = []
            context['weekly_hours'] = 0
            context['days_remaining'] = None
            context['is_overdue'] = False
            context['days_overdue'] = 0
            context['end_date_formatted'] = None
            context['weekly_breakdown'] = {}
            context['total_unique_logged_days'] = 0
            context['avg_hours_per_day'] = 0
            context['required_pace'] = 0
            context['current_pace'] = 0
            context['alert_status'] = 'info'
            context['alert_message'] = 'Complete your profile to get started.'
            context['days_since_last_log'] = None
            context['scheduled_hours_week'] = 0
            context['logged_hours_week'] = 0
            context['expected_hours_this_week'] = 0
            context['schedule_difference'] = 0
            context['schedule_status'] = 'none'
            context['working_days_remaining'] = None
        except Exception as e:
            # Catch any other errors
            context['profile'] = None
            context['completed_hours'] = 0
            context['remaining_hours'] = 0
            context['progress_percentage'] = 0
            context['stroke_dasharray'] = 0
            context['recent_logs'] = []
            context['weekly_hours'] = 0
            context['days_remaining'] = None
            context['is_overdue'] = False
            context['days_overdue'] = 0
            context['end_date_formatted'] = None
            context['weekly_breakdown'] = {}
            context['total_unique_logged_days'] = 0
            context['avg_hours_per_day'] = 0
            context['required_pace'] = 0
            context['current_pace'] = 0
            context['alert_status'] = 'error'
            context['alert_message'] = 'Error loading dashboard. Please try again.'
            context['days_since_last_log'] = None
            context['scheduled_hours_week'] = 0
            context['logged_hours_week'] = 0
            context['expected_hours_this_week'] = 0
            context['schedule_difference'] = 0
            context['schedule_status'] = 'none'
            context['working_days_remaining'] = None
            print(f"Dashboard error: {e}")
    
    elif is_supervisor(request.user):
        # Supervisor dashboard - for now, just shows account info
        context['role_name'] = 'Supervisor'
    
    elif is_admin(request.user):
        # Admin dashboard - for now, just shows account info
        context['role_name'] = 'Administrator'
    
    return render(request, 'dashboard.html', context)


@login_required
def profile(request):
    """View and edit user profile."""
    if not is_intern(request.user):
        messages.error(request, 'Only interns have profiles.')
        return redirect('dashboard')
    
    try:
        intern_profile = request.user.intern_profile
    except InternProfile.DoesNotExist:
        # Create if doesn't exist (shouldn't happen with signal handler)
        intern_profile, _ = InternProfile.objects.get_or_create(user=request.user)
    
    if request.method == 'POST':
        form = InternProfileForm(request.POST, instance=intern_profile)
        if form.is_valid():
            form.save()
            messages.success(request, 'Profile updated successfully!')
            return redirect('users:profile')
    else:
        form = InternProfileForm(instance=intern_profile)
    
    # Get or create schedule for all days of the week
    DAYS_OF_WEEK = ['monday', 'tuesday', 'wednesday', 'thursday', 'friday', 'saturday', 'sunday']
    schedule = {}
    for day in DAYS_OF_WEEK:
        day_schedule, _ = DaySchedule.objects.get_or_create(user=request.user, day_of_week=day)
        schedule[day] = day_schedule
    
    context = {
        'form': form,
        'profile': intern_profile,
        'schedule': schedule,
    }
    return render(request, 'users/profile.html', context)


@login_required
@require_http_methods(['POST'])
def update_profile(request):
    """Update personal information (first_name, last_name, email)."""
    first_name = request.POST.get('first_name', '').strip()
    last_name = request.POST.get('last_name', '').strip()
    email = request.POST.get('email', '').strip()
    
    # Validate email is not empty and is unique (except for current user)
    if not email:
        messages.error(request, 'Email cannot be empty.')
        return redirect('users:profile')
    
    if CustomUser.objects.filter(email=email).exclude(pk=request.user.pk).exists():
        messages.error(request, 'This email is already in use.')
        return redirect('users:profile')
    
    # Update user information
    request.user.first_name = first_name
    request.user.last_name = last_name
    request.user.email = email
    request.user.username = email  # Keep username in sync with email
    request.user.save()
    
    messages.success(request, 'Personal information updated successfully!')
    return redirect('users:profile')


@login_required
@require_http_methods(['POST'])
def update_schedule_bulk(request):
    """Update all days of the schedule in bulk."""
    if not is_intern(request.user):
        return redirect('dashboard')
    
    try:
        DAYS_OF_WEEK = ['monday', 'tuesday', 'wednesday', 'thursday', 'friday', 'saturday', 'sunday']
        
        for day in DAYS_OF_WEEK:
            day_schedule = DaySchedule.objects.get(user=request.user, day_of_week=day)
            
            # Check if day is marked as working
            is_working = f'is_working_day_{day}' in request.POST
            day_schedule.is_working_day = is_working
            
            # Only save times if it's a working day
            if is_working:
                start_time = request.POST.get(f'start_time_{day}')
                end_time = request.POST.get(f'end_time_{day}')
                
                if start_time:
                    day_schedule.start_time = start_time
                if end_time:
                    day_schedule.end_time = end_time
            else:
                # Clear times if not a working day
                day_schedule.start_time = None
                day_schedule.end_time = None
            
            day_schedule.save()
        
        messages.success(request, 'Schedule updated successfully!')
    except Exception as e:
        messages.error(request, f'Error updating schedule: {str(e)}')
    
    return redirect('users:profile')
