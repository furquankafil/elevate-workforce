from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from django.utils.html import format_html
from .models import CustomUser, CandidateProfile, EmployerProfile

class CustomUserAdmin(UserAdmin):
    """
    Extends standard Django User Admin to display roles, WhatsApp details, 
    and OTP parameters.
    """
    model = CustomUser
    list_display = ('email', 'username', 'first_name', 'last_name', 'is_candidate', 'is_employer', 'is_staff', 'is_phone_verified')
    list_filter = ('is_candidate', 'is_employer', 'is_staff', 'is_active', 'is_phone_verified')
    fieldsets = UserAdmin.fieldsets + (
        ('Recruitment Role Info', {'fields': ('is_candidate', 'is_employer', 'phone_number')}),
        ('Verification & OTP Details', {'fields': ('otp_code', 'otp_created_at', 'is_phone_verified')}),
    )
    add_fieldsets = UserAdmin.add_fieldsets + (
        ('Recruitment Role Info', {
            'classes': ('wide',),
            'fields': ('is_candidate', 'is_employer', 'phone_number', 'email'),
        }),
    )
    search_fields = ('email', 'username', 'phone_number', 'first_name', 'last_name')
    ordering = ('email',)


class CandidateProfileAdmin(admin.ModelAdmin):
    """
    Admin interface for candidate details, highlighting years of experience, 
    key skills, and resume downloads.
    """
    list_display = ('get_full_name', 'get_email', 'title', 'experience_years', 'current_location', 'view_resume_link')
    search_fields = ('user__first_name', 'user__last_name', 'user__email', 'title', 'skills')
    list_filter = ('experience_years', 'current_location')
    readonly_fields = ('created_at', 'updated_at')

    def get_full_name(self, obj):
        return obj.user.get_full_name() or obj.user.username
    get_full_name.short_description = "Candidate Name"

    def get_email(self, obj):
        return obj.user.email
    get_email.short_description = "Email Address"

    def view_resume_link(self, obj):
        if obj.resume:
            return format_html('<a href="{}" target="_blank" style="font-weight: bold; color: #00AEEF;">Download CV</a>', obj.resume.url)
        return "No CV Uploaded"
    view_resume_link.short_description = "Resume File"


class EmployerProfileAdmin(admin.ModelAdmin):
    """
    Admin layout for employer profiles, offering verification toggles 
    for managing job posting permissions.
    """
    list_display = ('company_name', 'get_email', 'industry', 'company_website', 'is_verified_employer', 'created_at')
    search_fields = ('company_name', 'user__email', 'industry', 'office_address')
    list_filter = ('industry', 'is_verified_employer')
    list_editable = ('is_verified_employer',)
    readonly_fields = ('created_at', 'updated_at')

    def get_email(self, obj):
        return obj.user.email
    get_email.short_description = "Owner Email"


# Registration
admin.site.register(CustomUser, CustomUserAdmin)
admin.site.register(CandidateProfile, CandidateProfileAdmin)
admin.site.register(EmployerProfile, EmployerProfileAdmin)