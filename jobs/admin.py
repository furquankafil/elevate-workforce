from django.contrib import admin
from django.utils.html import format_html
from .models import Destination, Category, Job, Application, Interview, SavedJob

class DestinationAdmin(admin.ModelAdmin):
    """
    Admin control layout for destination countries and key metropolitan hubs.
    """
    list_display = ('name', 'slug', 'flag_code', 'has_banner')
    prepopulated_fields = {'slug': ('name',)}
    search_fields = ('name', 'description')

    def has_banner(self, obj):
        return bool(obj.banner_image)
    has_banner.boolean = True
    has_banner.short_description = "Banner Image"


class CategoryAdmin(admin.ModelAdmin):
    """
    Admin control layout for industry sectors.
    """
    list_display = ('name', 'slug', 'icon_class')
    prepopulated_fields = {'slug': ('name',)}
    search_fields = ('name',)


class JobAdmin(admin.ModelAdmin):
    """
    Admin interface for job vacancy listings.
    Allows easy batch updates to vacancy statuses or featured flags.
    """
    list_display = ('title', 'employer', 'category', 'destination', 'job_type', 'vacancies', 'is_active', 'is_featured', 'expiry_date')
    list_filter = ('is_active', 'is_featured', 'job_type', 'destination', 'category')
    search_fields = ('title', 'employer__company_name', 'description', 'requirements')
    prepopulated_fields = {'slug': ('title',)}
    list_editable = ('is_active', 'is_featured', 'expiry_date')
    actions = ['make_active', 'make_inactive', 'mark_as_featured']
    readonly_fields = ('created_at',)

    def make_active(self, request, queryset):
        queryset.update(is_active=True)
        self.message_user(request, "Selected jobs successfully marked as active.")
    make_active.short_description = "Mark selected vacancies as Active"

    def make_inactive(self, request, queryset):
        queryset.update(is_active=False)
        self.message_user(request, "Selected jobs successfully marked as inactive.")
    make_inactive.short_description = "Mark selected vacancies as Inactive"

    def mark_as_featured(self, request, queryset):
        queryset.update(is_featured=True)
        self.message_user(request, "Selected jobs successfully set as Featured.")
    mark_as_featured.short_description = "Set selected vacancies as Featured"


class ApplicationAdmin(admin.ModelAdmin):
    """
    Administrative management interface for reviewing candidate applications.
    Displays direct linkages to download the submitted resume file snapshot.
    """
    list_display = ('get_candidate_name', 'job_title', 'get_employer_name', 'status', 'applied_at', 'view_resume_link')
    list_filter = ('status', 'applied_at', 'job__destination', 'job__category')
    search_fields = ('candidate__user__first_name', 'candidate__user__last_name', 'candidate__user__email', 'job__title')
    list_editable = ('status',)
    actions = ['shortlist_application', 'reject_application']

    def get_candidate_name(self, obj):
        return obj.candidate.user.get_full_name() or obj.candidate.user.email
    get_candidate_name.short_description = "Applicant Name"

    def job_title(self, obj):
        return obj.job.title
    job_title.short_description = "Applied Vacancy"

    def get_employer_name(self, obj):
        return obj.job.employer.company_name
    get_employer_name.short_description = "Employer"

    def view_resume_link(self, obj):
        if obj.resume:
            return format_html('<a href="{}" target="_blank" style="font-weight: bold; color: #00AEEF;">View Snapshot CV</a>', obj.resume.url)
        return "No File"
    view_resume_link.short_description = "Resume Snapshot"

    def shortlist_application(self, request, queryset):
        queryset.update(status='Shortlisted')
        self.message_user(request, "Selected applications set to Shortlisted.")
    shortlist_application.short_description = "Mark selected as Shortlisted"

    def reject_application(self, request, queryset):
        queryset.update(status='Rejected')
        self.message_user(request, "Selected applications set to Rejected.")
    reject_application.short_description = "Mark selected as Rejected"


class InterviewAdmin(admin.ModelAdmin):
    """
    Enables administrators to view scheduled panels and access links.
    """
    list_display = ('get_candidate', 'get_employer', 'interview_date', 'location_or_link')
    search_fields = ('application__candidate__user__email', 'application__job__title', 'location_or_link')
    list_filter = ('interview_date',)

    def get_candidate(self, obj):
        return obj.application.candidate
    get_candidate.short_description = "Candidate"

    def get_employer(self, obj):
        return obj.application.job.employer
    get_employer.short_description = "Employer"


class SavedJobAdmin(admin.ModelAdmin):
    """
    Tracks candidates' dynamic bookmark selections.
    """
    list_display = ('candidate', 'job', 'saved_at')
    search_fields = ('candidate__user__email', 'job__title')


# Registration
admin.site.register(Destination, DestinationAdmin)
admin.site.register(Category, CategoryAdmin)
admin.site.register(Job, JobAdmin)
admin.site.register(Application, ApplicationAdmin)
admin.site.register(Interview, InterviewAdmin)
admin.site.register(SavedJob, SavedJobAdmin)