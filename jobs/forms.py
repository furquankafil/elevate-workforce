from django import forms
from .models import Job, Interview

class JobForm(forms.ModelForm):
    """
    Form for corporate employers to post or modify job vacancies.
    """
    class Meta:
        model = Job
        fields = (
            'title', 'category', 'destination', 'job_type', 'salary_range', 
            'vacancies', 'experience_required', 'description', 
            'requirements', 'benefits', 'expiry_date', 'meta_title', 'meta_description'
        )
        widgets = {
            'title': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'E.g., Senior Structural Welder'}),
            'category': forms.Select(attrs={'class': 'form-select'}),
            'destination': forms.Select(attrs={'class': 'form-select'}),
            'job_type': forms.Select(attrs={'class': 'form-select'}),
            'salary_range': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'E.g., 4000 - 5500 AED / Month'}),
            'vacancies': forms.NumberInput(attrs={'class': 'form-control', 'min': 1}),
            'experience_required': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'E.g., 5+ Years'}),
            'description': forms.Textarea(attrs={'class': 'form-control', 'rows': 6, 'placeholder': 'Specify primary roles and operational duties...'}),
            'requirements': forms.Textarea(attrs={'class': 'form-control', 'rows': 5, 'placeholder': 'List essential technical certifications, licenses, or specific language skills...'}),
            'benefits': forms.Textarea(attrs={'class': 'form-control', 'rows': 4, 'placeholder': 'Accommodation, Airfare, Insurance, Overtime allowances...'}),
            'expiry_date': forms.DateInput(attrs={'class': 'form-control', 'type': 'date'}),
            'meta_title': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'SEO Title Tag for Google'}),
            'meta_description': forms.Textarea(attrs={'class': 'form-control', 'rows': 2, 'placeholder': 'SEO Meta Description for search engines'}),
        }


class InterviewForm(forms.ModelForm):
    """
    Form for scheduling candidate interviews.
    """
    class Meta:
        model = Interview
        fields = ('interview_date', 'location_or_link', 'notes')
        widgets = {
            'interview_date': forms.DateTimeInput(
                attrs={'class': 'form-control', 'type': 'datetime-local'}
            ),
            'location_or_link': forms.TextInput(
                attrs={'class': 'form-control', 'placeholder': 'E.g., Zoom Link, Google Meet, or New Delhi Head Office'}
            ),
            'notes': forms.Textarea(
                attrs={'class': 'form-control', 'rows': 4, 'placeholder': 'Provide specific guidelines regarding documentation, dress code, or panel details...'}
            ),
        }