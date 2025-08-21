"""
URL configuration for pawsitive_care project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/4.2/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static
from django.contrib.staticfiles.urls import staticfiles_urlpatterns
from . import views

urlpatterns = [
    path('admin/', admin.site.urls),
    path('accounts/', include('accounts.urls', namespace='accounts')),
    path('pets/', include('pets.urls', namespace='pets')),
    path('blog/', include('petmedia.urls', namespace='petmedia')),
    path('appointments/', include('appointments.urls', namespace='appointments')),
    path('billing/', include('billing.urls', namespace='billing')),
    path('communication/', include('communication.urls', namespace='communication')),
    path('inventory/', include('inventory.urls', namespace='inventory')),
    path('records/', include('records.urls', namespace='records')),
    path('', views.home_view, name='home'),  # Root URL with welcome page
    
    # Test URLs for error pages (remove in production)
    path('errors/', views.test_errors_page, name='test_errors'),
    path('safe-urls/', views.test_safe_urls, name='test_safe_urls'),
    path('404/', views.test_404_view, name='test_404'),
    path('500/', views.test_500_view, name='test_500'),
    path('403/', views.test_403_view, name='test_403'),
    path('400/', views.test_400_view, name='test_400'),
]

# Custom error handlers
handler404 = 'pawsitive_care.views.custom_404_view'
handler500 = 'pawsitive_care.views.custom_500_view'
handler403 = 'pawsitive_care.views.custom_403_view'
handler400 = 'pawsitive_care.views.custom_400_view'

# Serve media files in development
if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
    # Add staticfiles serving
    urlpatterns += staticfiles_urlpatterns()
    # Also add explicit static serving as backup
    urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)
