from django.db import models
from django.utils.text import slugify
from django.conf import settings

class SEOSetting(models.Model):
    """
    Global site SEO, analytics trackers, and meta schemas.
    """
    site_name = models.CharField(max_length=100, default="Elevate Workforce")
    default_meta_title = models.CharField(max_length=150, default="Elevate Workforce | Premier Overseas Recruitment")
    default_meta_description = models.TextField(
        default="Elevate Workforce is a leading international recruitment agency bridging skilled candidates with global industry opportunities."
    )
    google_analytics_id = models.CharField(max_length=50, blank=True, null=True)
    robots_txt = models.TextField(default="User-agent: *\nDisallow: /admin/\nDisallow: /users/dashboard/")
    schema_markup = models.TextField(blank=True, null=True)
    sitemap_enabled = models.BooleanField(default=True)

    class Meta:
        verbose_name = "SEO & System Settings"
        verbose_name_plural = "SEO & System Settings"

    def __str__(self):
        return f"Global SEO Configuration ({self.site_name})"


class BlogPost(models.Model):
    """
    CMS-driven recruitment advice and industry updates.
    """
    title = models.CharField(max_length=200)
    slug = models.SlugField(max_length=250, unique=True, blank=True)
    author = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, null=True, related_name='blog_posts')
    thumbnail = models.ImageField(upload_to='blogs/%Y/%m/', blank=True, null=True)
    content = models.TextField()
    is_published = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    meta_title = models.CharField(max_length=150, blank=True, null=True)
    meta_description = models.TextField(blank=True, null=True)

    class Meta:
        ordering = ['-created_at']

    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.title)
        super().save(*args, **kwargs)

    def __str__(self):
        return self.title


class GalleryItem(models.Model):
    """
    Dynamic photo library highlighting team successes.
    """
    CATEGORY_CHOICES = (
        ('recruitment', 'Recruitment Drive'),
        ('placed_candidates', 'Placed Candidates'),
        ('office', 'Office & Staff'),
        ('events', 'Corporate Events'),
    )

    title = models.CharField(max_length=150)
    image = models.ImageField(upload_to='gallery/')
    category = models.CharField(max_length=50, choices=CATEGORY_CHOICES, default='recruitment')
    caption = models.CharField(max_length=255, blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-created_at']

    def __str__(self):
        return self.title


class FAQ(models.Model):
    """
    Standard and relevant recruitment questions and answers.
    """
    question = models.CharField(max_length=255)
    answer = models.TextField()
    order = models.PositiveIntegerField(default=0)

    class Meta:
        ordering = ['order']

    def __str__(self):
        return self.question


class Testimonial(models.Model):
    """
    Testimonials from corporate employers or placed workers.
    """
    ROLE_CHOICES = (
        ('candidate', 'Placed Candidate'),
        ('employer', 'Corporate Partner / Client'),
    )

    name = models.CharField(max_length=100)
    role_type = models.CharField(max_length=20, choices=ROLE_CHOICES, default='candidate')
    designation = models.CharField(max_length=150)
    avatar = models.ImageField(upload_to='testimonials/', blank=True, null=True)
    feedback = models.TextField()
    rating = models.PositiveIntegerField(default=5)
    is_featured = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-created_at']

    def __str__(self):
        return f"{self.name} - {self.designation}"


class ContactMessage(models.Model):
    """
    Database logging of Contact Page inquiries.
    Updated to support an optional resume document upload.
    """
    name = models.CharField(max_length=100)
    email = models.EmailField()
    phone = models.CharField(max_length=25, blank=True, null=True)
    subject = models.CharField(max_length=200)
    message = models.TextField()
    resume = models.FileField(upload_to='contact_resumes/%Y/%m/', blank=True, null=True, help_text="Optional CV attachment")
    sent_at = models.DateTimeField(auto_now_add=True)
    is_resolved = models.BooleanField(default=False)
    admin_notes = models.TextField(blank=True, null=True)

    class Meta:
        ordering = ['-sent_at']

    def __str__(self):
        return f"Message from {self.name} - {self.subject}"


class NewsletterSubscriber(models.Model):
    """
    Newsletter email collections.
    """
    email = models.EmailField(unique=True)
    subscribed_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.email