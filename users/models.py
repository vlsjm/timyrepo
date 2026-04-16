from django.db import models
from django.contrib.auth.models import AbstractUser, Group
from django.db.models.signals import post_save
from django.dispatch import receiver


class CustomUser(AbstractUser):
    """
    Custom user model with role-based access control.
    Roles: Intern, Admin, Supervisor
    """
    
    ROLE_CHOICES = [
        ('intern', 'Intern'),
        ('admin', 'Admin'),
        ('supervisor', 'Supervisor'),
    ]
    
    role = models.CharField(max_length=20, choices=ROLE_CHOICES, default='intern')
    
    class Meta:
        verbose_name = 'User'
        verbose_name_plural = 'Users'
    
    def __str__(self):
        return f"{self.get_full_name()} ({self.get_role_display()})"
    
    def is_intern(self):
        return self.role == 'intern'
    
    def is_admin(self):
        return self.role == 'admin'
    
    def is_supervisor(self):
        return self.role == 'supervisor'
    
    def save(self, *args, **kwargs):
        """Override save to update groups based on role."""
        super().save(*args, **kwargs)
        
        # Map role to group
        role_group_map = {
            'intern': 'Intern',
            'supervisor': 'Supervisor',
            'admin': 'Admin',
        }
        
        # Remove user from all role groups
        role_groups = Group.objects.filter(name__in=['Intern', 'Supervisor', 'Admin'])
        self.groups.remove(*role_groups)
        
        # Add user to appropriate group
        if self.role in role_group_map:
            group, _ = Group.objects.get_or_create(name=role_group_map[self.role])
            self.groups.add(group)


class InternProfile(models.Model):
    """
    Extended profile for interns with company and course information.
    """
    user = models.OneToOneField(CustomUser, on_delete=models.CASCADE, related_name='intern_profile')
    course = models.CharField(max_length=255)
    company = models.CharField(max_length=255)
    department = models.CharField(max_length=255, blank=True)
    required_hours = models.IntegerField(default=0)
    start_date = models.DateField(null=True, blank=True)
    end_date = models.DateField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        verbose_name = 'Intern Profile'
        verbose_name_plural = 'Intern Profiles'
    
    def __str__(self):
        return f"{self.user.get_full_name()} - {self.company}"
    
    def completed_hours(self):
        """Calculate total completed hours (all statuses)."""
        from logging_app.models import HourLog
        logs = HourLog.objects.filter(intern=self.user)
        total = sum(log.total_hours() for log in logs)
        return total
    
    def remaining_hours(self):
        """Calculate remaining hours."""
        return max(0, self.required_hours - self.completed_hours())
    
    def progress_percentage(self):
        """Calculate progress as percentage."""
        if self.required_hours == 0:
            return 0
        return min(100, (self.completed_hours() / self.required_hours) * 100)


class SupervisorProfile(models.Model):
    """
    Extended profile for supervisors.
    Provisions for future expansion with team management.
    """
    user = models.OneToOneField(CustomUser, on_delete=models.CASCADE, related_name='supervisor_profile')
    department = models.CharField(max_length=255, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        verbose_name = 'Supervisor Profile'
        verbose_name_plural = 'Supervisor Profiles'
    
    def __str__(self):
        return f"Supervisor: {self.user.get_full_name()}"


class AdminProfile(models.Model):
    """
    Extended profile for admins.
    Provisions for future expansion with system management.
    """
    user = models.OneToOneField(CustomUser, on_delete=models.CASCADE, related_name='admin_profile')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        verbose_name = 'Admin Profile'
        verbose_name_plural = 'Admin Profiles'
    
    def __str__(self):
        return f"Admin: {self.user.get_full_name()}"


class DaySchedule(models.Model):
    """
    Model to store the weekly schedule for an intern.
    Each day of the week can have a start and end time.
    """
    
    DAYS_OF_WEEK = [
        ('monday', 'Monday'),
        ('tuesday', 'Tuesday'),
        ('wednesday', 'Wednesday'),
        ('thursday', 'Thursday'),
        ('friday', 'Friday'),
        ('saturday', 'Saturday'),
        ('sunday', 'Sunday'),
    ]
    
    user = models.ForeignKey(CustomUser, on_delete=models.CASCADE, related_name='schedule_days')
    day_of_week = models.CharField(max_length=20, choices=DAYS_OF_WEEK)
    start_time = models.TimeField(null=True, blank=True)
    end_time = models.TimeField(null=True, blank=True)
    is_working_day = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        unique_together = ('user', 'day_of_week')
        verbose_name = 'Day Schedule'
        verbose_name_plural = 'Day Schedules'
    
    def __str__(self):
        if self.is_working_day and self.start_time and self.end_time:
            return f"{self.user.get_full_name()} - {self.get_day_of_week_display()}: {self.start_time.strftime('%I:%M %p')} - {self.end_time.strftime('%I:%M %p')}"
        else:
            return f"{self.user.get_full_name()} - {self.get_day_of_week_display()}: Off"
    
    def total_hours(self):
        """Calculate total hours for the day."""
        if not self.is_working_day or not self.start_time or not self.end_time:
            return 0
        from datetime import datetime, timedelta
        dt_start = datetime.combine(datetime.today(), self.start_time)
        dt_end = datetime.combine(datetime.today(), self.end_time)
        
        if dt_end < dt_start:
            dt_end += timedelta(days=1)
        
        delta = dt_end - dt_start
        return delta.total_seconds() / 3600


# Signal handlers for automatic profile creation
@receiver(post_save, sender=CustomUser)
def create_user_profile(sender, instance, created, **kwargs):
    """Create appropriate profile when user is created."""
    if created:
        if instance.role == 'intern':
            InternProfile.objects.get_or_create(user=instance)
            # Create default schedule for all days of the week
            DAYS_OF_WEEK = ['monday', 'tuesday', 'wednesday', 'thursday', 'friday', 'saturday', 'sunday']
            for day in DAYS_OF_WEEK:
                DaySchedule.objects.get_or_create(user=instance, day_of_week=day)
        elif instance.role == 'supervisor':
            SupervisorProfile.objects.get_or_create(user=instance)
        elif instance.role == 'admin':
            AdminProfile.objects.get_or_create(user=instance)


@receiver(post_save, sender=CustomUser)
def save_user_profile(sender, instance, **kwargs):
    """Sync role changes with group membership."""
    # The group assignment happens in the save() method of CustomUser
    pass
