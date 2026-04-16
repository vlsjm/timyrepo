"""
URL configuration for internshiptracker project.
"""
from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static
from users.views import dashboard

urlpatterns = [
    path('admin/', admin.site.urls),  # Admin has built-in login protection
    path('dashboard/', dashboard, name='dashboard'),
    path('', include('users.urls')),
    path('logging/', include('logging_app.urls')),
    path('reports/', include('reports.urls')),
]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
    urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)
