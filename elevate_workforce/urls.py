"""
URL configuration for elevate_workforce project.
"""

from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static

# Custom error handler for 404 Not Found error
handler404 = 'core.views.custom_404_view'

urlpatterns = [
    # Django Administration Panel
    path('admin/', admin.site.urls),
    
    # App-Specific Router Connections
    path('', include('core.urls', namespace='core')),
    path('jobs/', include('jobs.urls', namespace='jobs')),
    path('users/', include('users.urls', namespace='users')),
]

# Serve media and static files in development mode
if settings.DEBUG:
    urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)