# core/forms.py
from django import forms
from .models import JobDescription, Resume

class JobDescriptionForm(forms.ModelForm):
    class Meta:
        model = JobDescription
        fields = ['title', 'text']
        widgets = {
            'text': forms.Textarea(attrs={'rows': 10}),
        }

class ResumeUploadForm(forms.ModelForm):
    class Meta:
        model = Resume
        fields = ['title', 'resume_file']