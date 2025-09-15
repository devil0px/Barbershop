"""
URL configuration for project project.

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

urlpatterns = [
    # Hidden admin path for security - change this to something unique
    path('secure-admin-panel-2024/', admin.site.urls),
    path('', include('home.urls')),
    # Custom accounts URLs - يجب أن تكون قبل allauth لإعطاء الأولوية للصفحات المخصصة
    path('accounts/', include('accounts.urls')),
    # Django-allauth URLs - بعد accounts.urls للصفحات المتبقية
    path('accounts/', include('allauth.urls')),
    path('barbershops/', include('barbershops.urls')),
    path('bookings/', include('bookings.urls')),
    path('reviews/', include('reviews.urls')),
    path('notifications/', include('notifications.urls')),
]

# Serve media files (images, uploads) and static files
# This is required for ngrok and development
if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
    urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)

# Custom error handlers for security (prevent information disclosure)
handler404 = 'project.views.custom_404_view'
handler500 = 'project.views.custom_500_view'
handler403 = 'project.views.custom_403_view'
