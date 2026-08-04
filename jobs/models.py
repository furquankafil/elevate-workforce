from django.db import models
from django.utils.text import slugify
from users.models import CandidateProfile, EmployerProfile

class Destination(models.Model):
    """
    Sourcing destinations (including countries and key metropolitan hubs)
    supported by Elevate Workforce. Includes SEO fields and custom descriptions.
    """
    name = models.CharField(max_length=100, unique=True)
    slug = models.SlugField(max_length=120, unique=True, blank=True)
    flag_code = models.CharField(max_length=10, blank=True, null=True, help_text="ISO Country Code (e.g. AE, SA, RO) or CSS flag class")
    banner_image = models.ImageField(upload_to='destinations/', blank=True, null=True)
    description = models.TextField(help_text="Detailed recruitment info for this destination")
    
    # SEO Settings per destination page
    meta_title = models.CharField(max_length=150, blank=True, null=True)
    meta_description = models.TextField(blank=True, null=True)
    
    class Meta:
        verbose_name_plural = "Destinations"
        ordering = ['name']

    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.name)
        super().save(*args, **kwargs)

    def __str__(self):
        return self.name


class Category(models.Model):
    """
    Job sectors/industries (e.g., Oil & Gas, Hospitality, Civil Engineering).
    """
    name = models.CharField(max_length=100, unique=True)
    slug = models.SlugField(max_length=120, unique=True, blank=True)
    icon_class = models.CharField(max_length=50, default="fa-briefcase", help_text="FontAwesome icon class name (e.g., fa-oil-well)")
    description = models.TextField(blank=True, null=True)

    class Meta:
        verbose_name_plural = "Categories"
        ordering = ['name']

    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.name)
        super().save(*args, **kwargs)

    def __str__(self):
        return self.name


class Job(models.Model):
    """
    Detailed Job Posting Schema mapped to Category and Destination.
    """
    JOB_TYPES = (
        ('Full-time', 'Full-time'),
        ('Contract', 'Contract'),
        ('Temporary', 'Temporary'),
        ('Rotational', 'Rotational'),
    )

    employer = models.ForeignKey(EmployerProfile, on_delete=models.CASCADE, related_name='jobs')
    title = models.CharField(max_length=200)
    slug = models.SlugField(max_length=250, unique=True, blank=True)
    
    # Made nullable to allow safe migrations without interactive prompts
    category = models.ForeignKey(Category, on_delete=models.PROTECT, related_name='jobs', null=True, blank=True)
    destination = models.ForeignKey(Destination, on_delete=models.PROTECT, related_name='jobs', null=True, blank=True)
    
    job_type = models.CharField(max_length=30, choices=JOB_TYPES, default='Full-time')
    
    # Financial and Job Details
    salary_range = models.CharField(max_length=100, blank=True, null=True, help_text="E.g., $3,000 - $4,500 USD / Month")
    vacancies = models.PositiveIntegerField(default=1)
    experience_required = models.CharField(max_length=100, help_text="E.g., 3-5 Years")
    
    # Core Descriptions
    description = models.TextField(help_text="Detailed job description and tasks")
    requirements = models.TextField(help_text="Required skills, certifications, and licenses")
    benefits = models.TextField(blank=True, null=True, help_text="Visa, accommodation, transport details")
    
    # Admin Controls
    is_active = models.BooleanField(default=True)
    is_featured = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)
    expiry_date = models.DateField(blank=True, null=True)
    
    # SEO Fields
    meta_title = models.CharField(max_length=150, blank=True, null=True)
    meta_description = models.TextField(blank=True, null=True)

    class Meta:
        ordering = ['-created_at']

    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.title)
        super().save(*args, **kwargs)

    def __str__(self):
        return f"{self.title} - {self.employer.company_name} ({self.destination.name if self.destination else 'N/A'})"


class Application(models.Model):
    """
    Tracks Candidate's formal applications to jobs.
    """
    STATUS_CHOICES = (
        ('Applied', 'Applied'),
        ('Shortlisted', 'Shortlisted'),
        ('Interview Scheduled', 'Interview Scheduled'),
        ('Rejected', 'Rejected'),
    )

    job = models.ForeignKey(Job, on_delete=models.CASCADE, related_name='applications')
    candidate = models.ForeignKey(CandidateProfile, on_delete=models.CASCADE, related_name='applications')
    resume = models.FileField(upload_to='application_resumes/%Y/%m/', help_text="CV snapshot active during submission time")
    cover_letter = models.TextField(blank=True, null=True)
    status = models.CharField(max_length=30, choices=STATUS_CHOICES, default='Applied')
    applied_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        unique_together = ('job', 'candidate')
        ordering = ['-applied_at']

    def __str__(self):
        return f"{self.candidate.user.get_full_name() or self.candidate.user.email} -> {self.job.title}"


class Interview(models.Model):
    """
    Recruitment Interview details scheduled by Verified Employers.
    """
    application = models.OneToOneField(Application, on_delete=models.CASCADE, related_name='interview')
    interview_date = models.DateTimeField()
    location_or_link = models.CharField(max_length=255, help_text="Online Meet Link, Zoom, or Office Address")
    notes = models.TextField(blank=True, null=True, help_text="Candidate instructions, timing or details")
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Interview for {self.application.candidate} on {self.interview_date}"


class SavedJob(models.Model):
    """
    Candidate bookmarks / saved listings.
    """
    candidate = models.ForeignKey(CandidateProfile, on_delete=models.CASCADE, related_name='saved_jobs')
    job = models.ForeignKey(Job, on_delete=models.CASCADE, related_name='saved_by_candidates')
    saved_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ('candidate', 'job')

    def __str__(self):
        return f"{self.candidate.user.email} saved {self.job.title}"