from django.contrib import admin
from .models import SEOSetting, BlogPost, GalleryItem, FAQ, Testimonial, ContactMessage, NewsletterSubscriber

class SEOSettingAdmin(admin.ModelAdmin):
    """
    Ensures that only one global system setting record exists.
    Prevents administrators from accidentally creating redundant configurations.
    """
    list_display = ('site_name', 'default_meta_title', 'sitemap_enabled')
    
    def has_add_permission(self, request):
        # Allow adding a configuration record only if none exist yet
        count = SEOSetting.objects.all().count()
        if count == 0:
            return True
        return False

    def has_delete_permission(self, request, obj=None):
        # Restrict standard record deletion to prevent breaking core lookups
        return False


class BlogPostAdmin(admin.ModelAdmin):
    """
    Admin control layout for corporate blog posts, with automated slug mapping.
    """
    list_display = ('title', 'author', 'is_published', 'created_at', 'updated_at')
    list_filter = ('is_published', 'created_at', 'author')
    search_fields = ('title', 'content', 'meta_title')
    prepopulated_fields = {'slug': ('title',)}
    list_editable = ('is_published',)
    readonly_fields = ('created_at', 'updated_at')

    def save_model(self, request, obj, form, change):
        # Automatically assign the logged-in administrator as author if unassigned
        if not obj.author:
            obj.author = request.user
        super().save_model(request, obj, form, change)


class GalleryItemAdmin(admin.ModelAdmin):
    """
    Admin control layout for success gallery elements.
    """
    list_display = ('title', 'category', 'created_at', 'has_image')
    list_filter = ('category', 'created_at')
    search_fields = ('title', 'caption')

    def has_image(self, obj):
        return bool(obj.image)
    has_image.boolean = True
    has_image.short_description = "Image Loaded"


class FAQAdmin(admin.ModelAdmin):
    """
    Admin interface for displaying and ordering frequently asked questions.
    """
    list_display = ('question', 'order')
    list_editable = ('order',)
    search_fields = ('question', 'answer')


class TestimonialAdmin(admin.ModelAdmin):
    """
    Admin interface for managing employer and candidate feedback.
    """
    list_display = ('name', 'role_type', 'designation', 'rating', 'is_featured')
    list_filter = ('role_type', 'rating', 'is_featured')
    search_fields = ('name', 'designation', 'feedback')
    list_editable = ('is_featured', 'rating')


class ContactMessageAdmin(admin.ModelAdmin):
    """
    Admin panel for processing contact page submissions.
    Makes contact messages read-only to preserve submission integrity,
    and adds actions to mark messages as resolved.
    """
    list_display = ('name', 'email', 'phone', 'subject', 'sent_at', 'is_resolved')
    list_filter = ('is_resolved', 'sent_at')
    search_fields = ('name', 'email', 'subject', 'message')
    list_editable = ('is_resolved',)
    readonly_fields = ('name', 'email', 'phone', 'subject', 'message', 'sent_at')
    actions = ['mark_as_resolved', 'mark_as_unresolved']

    def mark_as_resolved(self, request, queryset):
        queryset.update(is_resolved=True)
        self.message_user(request, "Selected inquiries successfully marked as resolved.")
    mark_as_resolved.short_description = "Mark selected as Resolved"

    def mark_as_unresolved(self, request, queryset):
        queryset.update(is_resolved=False)
        self.message_user(request, "Selected inquiries successfully marked as unresolved.")
    mark_as_unresolved.short_description = "Mark selected as Unresolved"


class NewsletterSubscriberAdmin(admin.ModelAdmin):
    """
    Tracks and exports subscription emails.
    """
    list_display = ('email', 'subscribed_at')
    search_fields = ('email',)
    readonly_fields = ('subscribed_at',)


# Registration
admin.site.register(SEOSetting, SEOSettingAdmin)
admin.site.register(BlogPost, BlogPostAdmin)
admin.site.register(GalleryItem, GalleryItemAdmin)
admin.site.register(FAQ, FAQAdmin)
admin.site.register(Testimonial, TestimonialAdmin)
admin.site.register(ContactMessage, ContactMessageAdmin)
admin.site.register(NewsletterSubscriber, NewsletterSubscriberAdmin)