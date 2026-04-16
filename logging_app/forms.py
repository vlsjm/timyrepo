from django import forms
from .models import HourLog


class HourLogForm(forms.ModelForm):
    """
    Form for creating/editing hour log entries with two logging modes.
    - Single: One period with automatic 1-hour break deduction
    - Split: Morning and afternoon (user already counted break)
    """
    
    class Meta:
        model = HourLog
        fields = ('date', 'logging_mode', 'time_in', 'time_out', 'time_in_afternoon', 'time_out_afternoon', 'description')
        widgets = {
            'date': forms.DateInput(attrs={
                'class': 'w-full p-3 border border-gray-300 rounded-lg',
                'type': 'date'
            }),
            'logging_mode': forms.RadioSelect(attrs={
                'class': 'logging-mode-selector'
            }),
            'time_in': forms.TimeInput(attrs={
                'class': 'w-full p-3 border border-gray-300 rounded-lg',
                'type': 'time'
            }),
            'time_out': forms.TimeInput(attrs={
                'class': 'w-full p-3 border border-gray-300 rounded-lg',
                'type': 'time'
            }),
            'time_in_afternoon': forms.TimeInput(attrs={
                'class': 'w-full p-3 border border-gray-300 rounded-lg',
                'type': 'time'
            }),
            'time_out_afternoon': forms.TimeInput(attrs={
                'class': 'w-full p-3 border border-gray-300 rounded-lg',
                'type': 'time'
            }),
            'description': forms.Textarea(attrs={
                'class': 'w-full p-3 border border-gray-300 rounded-lg',
                'rows': 4,
                'placeholder': 'Describe the tasks you completed...'
            }),
        }
    
    def clean(self):
        """Custom validation based on logging mode."""
        cleaned_data = super().clean()
        logging_mode = cleaned_data.get('logging_mode')
        time_in = cleaned_data.get('time_in')
        time_out = cleaned_data.get('time_out')
        time_in_afternoon = cleaned_data.get('time_in_afternoon')
        time_out_afternoon = cleaned_data.get('time_out_afternoon')
        
        # Morning times are always required
        if not time_in:
            self.add_error('time_in', 'Time in is required.')
        if not time_out:
            self.add_error('time_out', 'Time out is required.')
        
        # For split mode, if afternoon has one time, it needs both
        if logging_mode == 'split':
            if (time_in_afternoon or time_out_afternoon):
                if not time_in_afternoon:
                    self.add_error('time_in_afternoon', 'Afternoon time in is required if logging afternoon.')
                if not time_out_afternoon:
                    self.add_error('time_out_afternoon', 'Afternoon time out is required if logging afternoon.')
        
        return cleaned_data
    
    def save(self, commit=True):
        """Set break_deduction based on logging mode."""
        instance = super().save(commit=False)
        
        # Single mode always deducts 1 hour
        if instance.logging_mode == 'single':
            instance.break_deduction = 'one_hour'
            # Clear afternoon fields for single mode
            instance.time_in_afternoon = None
            instance.time_out_afternoon = None
        # Split mode doesn't deduct
        elif instance.logging_mode == 'split':
            instance.break_deduction = 'none'
        
        if commit:
            instance.save()
        return instance
