from django.db import models
from django.contrib.auth.models import AbstractUser
from django.utils.translation import gettext_lazy as _

class CustomUser(AbstractUser):
    """
    Custom user model to handle unified login across different roles.
    We enforce unique emails and add flags for Candidates and Employers.
    """
    email = models.EmailField(_('email address'), unique=True)
    phone_number = models.CharField(max_length=20, blank=True, null=True)
    is_candidate = models.BooleanField(default=False, verbose_name="Is Candidate")
    is_employer = models.BooleanField(default=False, verbose_name="Is Employer")
    
    # Ready for OTP verification
    otp_code = models.CharField(max_length=6, blank=True, null=True)
    otp_created_at = models.DateTimeField(blank=True, null=True)
    is_phone_verified = models.BooleanField(default=False)

    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = ['username']

    def __str__(self):
        return self.email


class CandidateProfile(models.Model):
    """
    Profile extension for recruitment candidates.
    Stores professional resumes, skill matrices, and dashboard data.
    """
    user = models.OneToOneField(CustomUser, on_delete=models.CASCADE, related_name='candidate_profile')
    title = models.CharField(max_length=150, blank=True, null=True, help_text="Current Job Title or Specialization")
    bio = models.TextField(blank=True, null=True, help_text="Short professional summary")
    resume = models.FileField(upload_to='resumes/%Y/%m/', blank=True, null=True)
    skills = models.TextField(blank=True, null=True, help_text="Comma-separated skills (e.g. Piping Engineering, HSE, HVAC)")
    experience_years = models.PositiveIntegerField(default=0)
    current_location = models.CharField(max_length=100, blank=True, null=True)
    preferred_countries = models.TextField(blank=True, null=True, help_text="Target locations separated by commas")
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def get_skills_list(self):
        if self.skills:
            return [s.strip() for s in self.skills.split(',') if s.strip()]
        return []

    def __str__(self):
        return f"Candidate: {self.user.get_full_name() or self.user.email}"


class EmployerProfile(models.Model):
    """
    Profile representation for international or regional employers.
    Enables job postings, application screening, and candidate tracking.
    """
    user = models.OneToOneField(CustomUser, on_delete=models.CASCADE, related_name='employer_profile')
    company_name = models.CharField(max_length=200)
    company_logo = models.ImageField(upload_to='employer_logos/%Y/%m/', blank=True, null=True)
    company_website = models.URLField(blank=True, null=True)
    industry = models.CharField(max_length=100, help_text="E.g., Oil & Gas, Healthcare, Construction")
    company_description = models.TextField(blank=True, null=True)
    office_address = models.TextField(blank=True, null=True)
    is_verified_employer = models.BooleanField(default=False, help_text="Indicates if admin has verified the employer credential")
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.company_name