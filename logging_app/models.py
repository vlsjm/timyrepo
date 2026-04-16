from django.db import models
from django.contrib.auth import get_user_model
from datetime import datetime, timedelta

User = get_user_model()


class HourLog(models.Model):
    """
    Model for logging daily work hours.
    Supports two logging modes: single period with auto break deduction or split morning/afternoon.
    """
    
    STATUS_CHOICES = [
        ('draft', 'Draft'),
        ('submitted', 'Submitted'),
        ('approved', 'Approved'),
        ('rejected', 'Rejected'),
    ]
    
    LOG_MODE_CHOICES = [
        ('single', 'Single Period (Auto 1-hour break deduction)'),
        ('split', 'Split Shift (Morning & Afternoon)'),
    ]
    
    BREAK_CHOICES = [
        ('none', 'No break deduction'),
        ('one_hour', 'Deduct 1 hour for break'),
    ]
    
    intern = models.ForeignKey(User, on_delete=models.CASCADE, related_name='hour_logs')
    date = models.DateField()
    
    # Logging mode
    logging_mode = models.CharField(max_length=20, choices=LOG_MODE_CHOICES, default='split')
    
    # Single period (used when logging_mode='single')
    time_in = models.TimeField()
    time_out = models.TimeField()
    
    # Split shift fields (used when logging_mode='split')
    time_in_afternoon = models.TimeField(null=True, blank=True)
    time_out_afternoon = models.TimeField(null=True, blank=True)
    
    # Break deduction option (only for split mode)
    break_deduction = models.CharField(max_length=20, choices=BREAK_CHOICES, default='one_hour')
    
    description = models.TextField(help_text='Description of tasks completed')
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='draft')
    
    # Optional supervisor review
    reviewed_by = models.ForeignKey(
        User,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='reviewed_logs',
        limit_choices_to={'role__in': ['supervisor', 'admin']}
    )
    review_notes = models.TextField(blank=True)
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        unique_together = ('intern', 'date')
        ordering = ['-date']
        verbose_name = 'Hour Log'
        verbose_name_plural = 'Hour Logs'
    
    def __str__(self):
        return f"{self.intern.get_full_name()} - {self.date}"
    
    def total_hours(self):
        """Calculate total hours based on logging mode."""
        total = 0
        date = self.date
        
        if self.logging_mode == 'single':
            # Single period mode: calculate once and deduct 1 hour for break
            if self.time_in and self.time_out:
                dt_in = datetime.combine(date, self.time_in)
                dt_out = datetime.combine(date, self.time_out)
                
                if dt_out < dt_in:
                    dt_out += timedelta(days=1)
                
                delta = dt_out - dt_in
                total = delta.total_seconds() / 3600
                # Always deduct 1 hour for break in single mode
                total = max(0, total - 1)
        
        elif self.logging_mode == 'split':
            # Split shift mode: calculate morning + afternoon (user already counted break)
            # Morning shift
            if self.time_in and self.time_out:
                dt_in = datetime.combine(date, self.time_in)
                dt_out = datetime.combine(date, self.time_out)
                
                if dt_out < dt_in:
                    dt_out += timedelta(days=1)
                
                delta = dt_out - dt_in
                total += delta.total_seconds() / 3600
            
            # Afternoon shift
            if self.time_in_afternoon and self.time_out_afternoon:
                dt_in_after = datetime.combine(date, self.time_in_afternoon)
                dt_out_after = datetime.combine(date, self.time_out_afternoon)
                
                if dt_out_after < dt_in_after:
                    dt_out_after += timedelta(days=1)
                
                delta_after = dt_out_after - dt_in_after
                total += delta_after.total_seconds() / 3600
            
            # No automatic deduction in split mode - user already counted break
        
        return round(total, 2)
    
    def is_editable(self):
        """Check if log can be edited."""
        return self.status == 'draft'
    
    def can_submit(self):
        """Check if log can be submitted."""
        return self.status == 'draft' and self.total_hours() > 0
    
    def can_approve(self):
        """Check if log can be approved."""
        return self.status == 'submitted'
    
    def can_reject(self):
        """Check if log can be rejected."""
        return self.status in ['submitted', 'approved']


class WeeklyLog(models.Model):
    """
    Model for weekly summaries (optional, for optimization).
    """
    intern = models.ForeignKey(User, on_delete=models.CASCADE, related_name='weekly_logs')
    week_start = models.DateField()
    week_end = models.DateField()
    total_hours = models.DecimalField(max_digits=5, decimal_places=2, default=0)
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        unique_together = ('intern', 'week_start')
        ordering = ['-week_start']
        verbose_name = 'Weekly Log'
        verbose_name_plural = 'Weekly Logs'
    
    def __str__(self):
        return f"{self.intern.get_full_name()} - Week of {self.week_start}"
