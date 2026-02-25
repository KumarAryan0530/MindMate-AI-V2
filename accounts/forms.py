from .models import Profile
from django import forms


class ProfileForm(forms.ModelForm):
    class Meta:
        model = Profile
        fields = [
            'first_name', 
            'last_name', 
            'image', 
            'email',
            'phone_number',
            'date_of_birth', 
            'height', 
            'weight',
            'Blood_Group'
        ]
        exclude = ['user', 'id']
        widgets = {
            'first_name': forms.TextInput(attrs={
                'class': 'form-input',
                'placeholder': 'Enter your first name'
            }),
            'last_name': forms.TextInput(attrs={
                'class': 'form-input',
                'placeholder': 'Enter your last name'
            }),
            'email': forms.EmailInput(attrs={
                'class': 'form-input',
                'placeholder': 'Enter your email'
            }),
            'phone_number': forms.TextInput(attrs={
                'class': 'form-input',
                'placeholder': '+919876543210',
                'pattern': r'\+?[1-9]\d{1,14}',
                'title': 'Enter phone number with country code (e.g., +919876543210)'
            }),
            'date_of_birth': forms.DateInput(attrs={
                'class': 'form-input',
                'type': 'date',
                'max': '2020-12-31',  # Max date for reasonable age
                'min': '1920-01-01'   # Min date for reasonable age
            }),
            'height': forms.NumberInput(attrs={
                'class': 'form-input',
                'placeholder': 'Height in cm',
                'step': '0.1'
            }),
            'weight': forms.NumberInput(attrs={
                'class': 'form-input',
                'placeholder': 'Weight in kg',
                'step': '0.1'
            }),
            'Blood_Group': forms.TextInput(attrs={
                'class': 'form-input',
                'placeholder': 'e.g., A+, B-, O+',
                'maxlength': '10'
            }),
        }
        labels = {
            'date_of_birth': 'Date of Birth',
            'height': 'Height (cm)',
            'weight': 'Weight (kg)',
            'phone_number': 'Phone Number',
            'Blood_Group': 'Blood Group',
        }
        help_texts = {
            'date_of_birth': 'Your age will be calculated automatically from this date',
            'phone_number': 'Required for wellness call feature. Include country code (e.g., +919876543210)',
            'Blood_Group': 'Your blood group (optional)',
        }