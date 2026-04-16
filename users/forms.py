from django import forms
from django.contrib.auth.forms import UserCreationForm, UserChangeForm
from .models import CustomUser, InternProfile, DaySchedule


class CustomUserCreationForm(UserCreationForm):
    """
    Form for creating a new user account.
    """
    email = forms.EmailField(required=True, widget=forms.EmailInput(attrs={
        'class': 'w-full p-3 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500',
        'placeholder': 'Email'
    }))
    
    class Meta:
        model = CustomUser
        fields = ('email', 'first_name', 'last_name', 'password1', 'password2')
        widgets = {
            'first_name': forms.TextInput(attrs={
                'class': 'w-full p-3 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500',
                'placeholder': 'First Name'
            }),
            'last_name': forms.TextInput(attrs={
                'class': 'w-full p-3 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500',
                'placeholder': 'Last Name'
            }),
        }
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['password1'].widget.attrs.update({
            'class': 'w-full p-3 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500',
            'placeholder': 'Password'
        })
        self.fields['password2'].widget.attrs.update({
            'class': 'w-full p-3 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500',
            'placeholder': 'Confirm Password'
        })
    
    def clean_email(self):
        """Validate that email is unique (since it becomes the username)."""
        email = self.cleaned_data.get('email')
        if email and CustomUser.objects.filter(email=email).exists():
            raise forms.ValidationError('This email is already registered.')
        return email


class InternProfileForm(forms.ModelForm):
    """
    Form for creating/updating intern profile.
    """
    class Meta:
        model = InternProfile
        fields = ('course', 'company', 'department', 'required_hours', 'start_date', 'end_date')
        widgets = {
            'course': forms.TextInput(attrs={
                'class': 'w-full p-3 border border-gray-300 rounded-lg',
                'placeholder': 'e.g., Computer Science'
            }),
            'company': forms.TextInput(attrs={
                'class': 'w-full p-3 border border-gray-300 rounded-lg',
                'placeholder': 'e.g., Tech Company Inc'
            }),
            'department': forms.TextInput(attrs={
                'class': 'w-full p-3 border border-gray-300 rounded-lg',
                'placeholder': 'e.g., Engineering, HR, Marketing'
            }),
            'required_hours': forms.NumberInput(attrs={
                'class': 'w-full p-3 border border-gray-300 rounded-lg',
                'placeholder': 'e.g., 120',
                'min': '1'
            }),
            'start_date': forms.DateInput(attrs={
                'class': 'w-full p-3 border border-gray-300 rounded-lg',
                'type': 'date'
            }),
            'end_date': forms.DateInput(attrs={
                'class': 'w-full p-3 border border-gray-300 rounded-lg',
                'type': 'date'
            }),
        }


class DayScheduleForm(forms.ModelForm):
    """
    Form for editing a single day's schedule.
    """
    class Meta:
        model = DaySchedule
        fields = ('day_of_week', 'is_working_day', 'start_time', 'end_time')
        widgets = {
            'day_of_week': forms.Select(attrs={
                'class': 'w-full p-3 border border-gray-300 rounded-lg',
                'disabled': 'disabled'  # Disable to prevent changing day of week
            }),
            'is_working_day': forms.CheckboxInput(attrs={
                'class': 'h-4 w-4'
            }),
            'start_time': forms.TimeInput(attrs={
                'class': 'w-full p-3 border border-gray-300 rounded-lg',
                'type': 'time'
            }),
            'end_time': forms.TimeInput(attrs={
                'class': 'w-full p-3 border border-gray-300 rounded-lg',
                'type': 'time'
            }),
        }


class ScheduleFormSet(forms.BaseModelFormSet):
    """
    FormSet for managing the entire weekly schedule at once.
    """
    pass

