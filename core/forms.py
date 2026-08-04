from django import forms
from .models import ContactMessage
from django.core.exceptions import ValidationError

class ContactForm(forms.ModelForm):
    """
    Form for site visitors and candidate inquiries.
    """
    class Meta:
        model = ContactMessage
        fields = ('name', 'email', 'phone', 'subject', 'message', 'resume')
        widgets = {
            'name': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Enter your full name'}),
            'email': forms.EmailInput(attrs={'class': 'form-control', 'placeholder': 'Enter your active email'}),
            'phone': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'E.g., +91 98979 20091'}),
            'subject': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'How can we help you?'}),
            'message': forms.Textarea(attrs={'class': 'form-control', 'rows': 5, 'placeholder': 'Type your message details here...'}),
            'resume': forms.FileInput(attrs={'class': 'form-control'}),
        }

    def clean_phone(self):
        phone = self.cleaned_data.get('phone')
        if phone:
            clean = "".join(c for c in phone if c.isdigit() or c in ['+', ' ', '-'])
            if len(clean) < 7:
                raise forms.ValidationError("Please enter a valid phone number.")
            return clean
        return phone

    def clean_resume(self):
        resume = self.cleaned_data.get('resume')
        if resume:
            if resume.size > 5 * 1024 * 1024:
                raise ValidationError("Resume file size must not exceed 5MB.")
            extension = resume.name.split('.')[-1].lower()
            if extension not in ['pdf', 'doc', 'docx']:
                raise ValidationError("Only PDF or Word documents (.doc, .docx) are accepted.")
        return resume