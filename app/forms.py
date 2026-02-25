
from django import forms
from .models import JournalEntry, Prescription
PHQ_CHOICES = [
    (0, 'Not at all'),
    (1, 'Several days'),
    (2, 'More than half the days'),
    (3, 'Nearly every day'),
]

class PHQ9Form(forms.Form):
    q1 = forms.ChoiceField(choices=PHQ_CHOICES, widget=forms.RadioSelect, label="Little interest or pleasure in doing things?")
    q2 = forms.ChoiceField(choices=PHQ_CHOICES, widget=forms.RadioSelect, label="Feeling down, depressed, or hopeless?")
    q3 = forms.ChoiceField(choices=PHQ_CHOICES, widget=forms.RadioSelect, label="Trouble falling or staying asleep, or sleeping too much?")
    q4 = forms.ChoiceField(choices=PHQ_CHOICES, widget=forms.RadioSelect, label="Feeling tired or having little energy?")
    q5 = forms.ChoiceField(choices=PHQ_CHOICES, widget=forms.RadioSelect, label="Poor appetite or overeating?")
    q6 = forms.ChoiceField(choices=PHQ_CHOICES, widget=forms.RadioSelect, label="Feeling bad about yourself or that you are a failure?")
    q7 = forms.ChoiceField(choices=PHQ_CHOICES, widget=forms.RadioSelect, label="Trouble concentrating on things?")
    q8 = forms.ChoiceField(choices=PHQ_CHOICES, widget=forms.RadioSelect, label="Moving or speaking so slowly that others could have noticed?")
    q9 = forms.ChoiceField(choices=PHQ_CHOICES, widget=forms.RadioSelect, label="Thoughts that you would be better off dead?")


# forms.py



        


class ConsultationBookingForm(forms.Form):
    first_name = forms.CharField(max_length=100, required=True)
    last_name = forms.CharField(max_length=100, required=True)
    email = forms.EmailField(required=True)
    phone = forms.CharField(max_length=15, required=True)
    date = forms.DateField(widget=forms.SelectDateWidget(), required=True)
    time = forms.TimeField(widget=forms.TimeInput(attrs={'type': 'time'}), required=True)
    message = forms.CharField(widget=forms.Textarea, required=False)

# forms.py



class JournalForm(forms.ModelForm):
    class Meta:
        model = JournalEntry
        fields = ['content']
        widgets = {
            'content': forms.Textarea(attrs={
                'class': 'form-control',
                'rows': 5,
                'placeholder': 'Write about your day...'
            })
        }


class PrescriptionForm(forms.ModelForm):
    class Meta:
        model = Prescription
        fields = ['prescription_image', 'prescription_file']
        widgets = {
            'prescription_image': forms.FileInput(attrs={
                'class': 'form-control',
                'accept': 'image/*'
            }),
            'prescription_file': forms.FileInput(attrs={
                'class': 'form-control',
                'accept': 'application/pdf,image/*'
            })
        }
    
    def clean(self):
        cleaned_data = super().clean()
        image = cleaned_data.get('prescription_image')
        file = cleaned_data.get('prescription_file')
        
        if not image and not file:
            raise forms.ValidationError("Please upload either an image or a PDF file.")
        
        if image and file:
            raise forms.ValidationError("Please upload only one file (either image or PDF).")
        
        # Validate file size (4MB limit)
        file_to_check = image or file
        if file_to_check and file_to_check.size > 4 * 1024 * 1024:
            raise forms.ValidationError("File size must be under 4MB.")
        
        return cleaned_data