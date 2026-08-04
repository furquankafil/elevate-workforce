from .models import SEOSetting

def seo_settings(request):
    """
    Safely injects the global SEOSetting record into all templates.
    Includes database exception fallbacks to ensure the site runs cleanly 
    even before first migrations are executed.
    """
    try:
        # Fetch the active global SEO configuration
        settings = SEOSetting.objects.first()
    except Exception:
        # Fallback if database table does not exist yet (e.g. during initial setup)
        settings = None
        
    return {
        'seo_settings': settings
    }