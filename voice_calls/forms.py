from django import forms
from .models import VoiceCallSchedule
from django.utils import timezone
from datetime import timedelta


class ScheduleCallForm(forms.ModelForm):
    class Meta:
        model = VoiceCallSchedule
        fields = ['scheduled_time', 'custom_prompt', 'first_message']
        widgets = {
            'scheduled_time': forms.DateTimeInput(
                attrs={
                    'type': 'datetime-local',
                    'class': 'form-control',
                    'min': timezone.now().strftime('%Y-%m-%dT%H:%M')
                }
            ),
            'custom_prompt': forms.Textarea(
                attrs={
                    'class': 'form-control',
                    'rows': 3,
                    'placeholder': 'Optional: e.g., "Focus on stress management and work-life balance"'
                }
            ),
            'first_message': forms.Textarea(
                attrs={
                    'class': 'form-control',
                    'rows': 2,
                    'placeholder': 'Optional: Custom greeting message'
                }
            ),
        }
        labels = {
            'scheduled_time': 'When would you like to receive the call?',
            'custom_prompt': 'Custom Focus (Optional)',
            'first_message': 'Custom Greeting (Optional)',
        }
        help_texts = {
            'scheduled_time': 'Select a date and time for your wellness check-in call',
            'custom_prompt': 'Specify what you\'d like to focus on during the call',
            'first_message': 'Customize the AI\'s opening message',
        }
    
    def clean_scheduled_time(self):
        scheduled_time = self.cleaned_data.get('scheduled_time')
        
        if not scheduled_time:
            raise forms.ValidationError("Please select a date and time for the call")
        
        # Ensure scheduled time is in the future
        if scheduled_time <= timezone.now():
            raise forms.ValidationError("Call must be scheduled for a future time")
        
        # Ensure scheduled time is not too far in the future (e.g., max 30 days)
        max_future = timezone.now() + timedelta(days=30)
        if scheduled_time > max_future:
            raise forms.ValidationError("Call cannot be scheduled more than 30 days in advance")
        
        return scheduled_time
