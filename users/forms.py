from django import forms
from django.contrib.auth.forms import UserCreationForm, AuthenticationForm
from django.contrib.auth import get_user_model
from django.core.exceptions import ValidationError

from .models import CustomUser, CandidateProfile, EmployerProfile

User = get_user_model()


class CandidateRegisterForm(UserCreationForm):
    """
    Candidate onboarding registration form.
    Creates CustomUser instances and sets the 'is_candidate' role to True.
    """
    first_name = forms.CharField(max_length=50, required=True, label="First Name")
    last_name = forms.CharField(max_length=50, required=True, label="Last Name")
    email = forms.EmailField(required=True, label="Email Address")
    phone_number = forms.CharField(max_length=20, required=True, label="WhatsApp / Phone Number")

    class Meta(UserCreationForm.Meta):
        model = User
        fields = ('email', 'username', 'first_name', 'last_name', 'phone_number')

    def clean_email(self):
        email = self.cleaned_data.get('email').lower()
        if User.objects.filter(email=email).exists():
            raise ValidationError("An account with this email address already exists.")
        return email

    def save(self, commit=True):
        user = super().save(commit=False)
        user.is_candidate = True
        user.email = self.cleaned_data['email']
        user.first_name = self.cleaned_data['first_name']
        user.last_name = self.cleaned_data['last_name']
        user.phone_number = self.cleaned_data['phone_number']
        if commit:
            user.save()
            # Generate Candidate Profile record automatically
            CandidateProfile.objects.get_or_create(user=user)
        return user


class EmployerRegisterForm(UserCreationForm):
    """
    Employer registration form.
    Creates CustomUser instances, sets the 'is_employer' role to True,
    and captures details for the associated Employer Profile.
    """
    company_name = forms.CharField(max_length=200, required=True, label="Company / Corporate Name")
    first_name = forms.CharField(max_length=50, required=True, label="HR Contact First Name")
    last_name = forms.CharField(max_length=50, required=True, label="HR Contact Last Name")
    email = forms.EmailField(required=True, label="Corporate Email")
    phone_number = forms.CharField(max_length=20, required=True, label="Business Phone Number")

    class Meta(UserCreationForm.Meta):
        model = User
        fields = ('email', 'username', 'first_name', 'last_name', 'phone_number')

    def clean_email(self):
        email = self.cleaned_data.get('email').lower()
        if User.objects.filter(email=email).exists():
            raise ValidationError("An account with this corporate email already exists.")
        return email

    def save(self, commit=True):
        user = super().save(commit=False)
        user.is_employer = True
        user.email = self.cleaned_data['email']
        user.first_name = self.cleaned_data['first_name']
        user.last_name = self.cleaned_data['last_name']
        user.phone_number = self.cleaned_data['phone_number']
        if commit:
            user.save()
            # Generate Employer Profile with company metadata
            EmployerProfile.objects.create(
                user=user,
                company_name=self.cleaned_data['company_name']
            )
        return user


class CustomLoginForm(AuthenticationForm):
    """
    Consolidated authentication form checking email instead of username.
    """
    username = forms.EmailField(widget=forms.EmailInput(attrs={
        'class': 'form-control',
        'placeholder': 'Enter registered email address',
        'autofocus': True
    }), label="Email Address")
    
    password = forms.CharField(widget=forms.PasswordInput(attrs={
        'class': 'form-control',
        'placeholder': 'Enter your password'
    }))


class UserUpdateForm(forms.ModelForm):
    """
    Form to manage unified core account parameters like name and phone numbers.
    """
    class Meta:
        model = User
        fields = ('first_name', 'last_name', 'phone_number')
        widgets = {
            'first_name': forms.TextInput(attrs={'class': 'form-control'}),
            'last_name': forms.TextInput(attrs={'class': 'form-control'}),
            'phone_number': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'WhatsApp Contact'}),
        }


class CandidateProfileForm(forms.ModelForm):
    """
    Forms handling CV file loads, experience inputs, and skill matrices.
    """
    class Meta:
        model = CandidateProfile
        fields = ('title', 'bio', 'resume', 'skills', 'experience_years', 'current_location', 'preferred_countries')
        widgets = {
            'title': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'E.g., Senior Piping Engineer'}),
            'bio': forms.Textarea(attrs={'class': 'form-control', 'rows': 3, 'placeholder': 'Summarize your career highlights...'}),
            'resume': forms.FileInput(attrs={'class': 'form-control'}),
            'skills': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Piping, Quality Assurance, Welding (separated by commas)'}),
            'experience_years': forms.NumberInput(attrs={'class': 'form-control'}),
            'current_location': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'E.g., Mumbai, India'}),
            'preferred_countries': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'E.g., Dubai, Saudi Arabia, Qatar'}),
        }

    def clean_resume(self):
        resume = self.cleaned_data.get('resume')
        if resume:
            # Validate file size (e.g., maximum 5MB limit)
            if resume.size > 5 * 1024 * 1024:
                raise ValidationError("Resume file size must not exceed 5MB.")
            # Validate file extension
            extension = resume.name.split('.')[-1].lower()
            if extension not in ['pdf', 'doc', 'docx']:
                raise ValidationError("Only PDF or Word documents (.doc, .docx) are accepted.")
        return resume


class EmployerProfileForm(forms.ModelForm):
    """
    Form to manage corporate identity, descriptions, websites, and logos.
    """
    class Meta:
        model = EmployerProfile
        fields = ('company_name', 'company_logo', 'company_website', 'industry', 'company_description', 'office_address')
        widgets = {
            'company_name': forms.TextInput(attrs={'class': 'form-control'}),
            'company_logo': forms.FileInput(attrs={'class': 'form-control'}),
            'company_website': forms.URLInput(attrs={'class': 'form-control', 'placeholder': 'https://example.com'}),
            'industry': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'E.g., Oil & Gas / Construction'}),
            'company_description': forms.Textarea(attrs={'class': 'form-control', 'rows': 4}),
            'office_address': forms.Textarea(attrs={'class': 'form-control', 'rows': 2}),
        }