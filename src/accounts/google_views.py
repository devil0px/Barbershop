#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Views للتعامل مع Google OAuth و One Tap Sign-In
"""
import json
from django.shortcuts import render, redirect
from django.http import JsonResponse
from django.contrib.auth import login, get_user_model
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_http_methods
from django.contrib import messages
from django.conf import settings
import logging

# إعداد Google OAuth
try:
    from google.oauth2 import id_token
    from google.auth.transport import requests
    GOOGLE_AUTH_AVAILABLE = True
except ImportError:
    GOOGLE_AUTH_AVAILABLE = False
    logging.warning("Google auth libraries not installed. Run: pip install google-auth")

User = get_user_model()
logger = logging.getLogger(__name__)

@csrf_exempt
@require_http_methods(["POST"])
def google_one_tap_login(request):
    """
    التعامل مع Google One Tap Sign-In
    """
    if not GOOGLE_AUTH_AVAILABLE:
        return JsonResponse({
            'success': False, 
            'error': 'Google authentication not available'
        })
    
    try:
        # الحصول على التوكن من الطلب
        credential = request.POST.get('credential')
        if not credential:
            return JsonResponse({
                'success': False, 
                'error': 'No credential provided'
            })
        
        # التحقق من صحة التوكن
        client_id = getattr(settings, 'GOOGLE_ONE_TAP_CLIENT_ID', None)
        if not client_id:
            return JsonResponse({
                'success': False, 
                'error': 'Google Client ID not configured'
            })
        
        # فك تشفير التوكن والتحقق منه
        idinfo = id_token.verify_oauth2_token(
            credential, 
            requests.Request(), 
            client_id
        )
        
        # التحقق من أن التوكن صادر من Google
        if idinfo['iss'] not in ['accounts.google.com', 'https://accounts.google.com']:
            return JsonResponse({
                'success': False, 
                'error': 'Invalid token issuer'
            })
        
        # استخراج معلومات المستخدم
        email = idinfo.get('email')
        name = idinfo.get('name', '')
        given_name = idinfo.get('given_name', '')
        family_name = idinfo.get('family_name', '')
        picture = idinfo.get('picture', '')
        
        if not email:
            return JsonResponse({
                'success': False, 
                'error': 'No email in token'
            })
        
        # البحث عن المستخدم أو إنشاؤه
        user, created = User.objects.get_or_create(
            email=email,
            defaults={
                'username': email,
                'first_name': given_name,
                'last_name': family_name,
                'is_email_verified': True,  # Google emails are verified
                'is_active': True,
                'user_type': 'customer',  # افتراضي
            }
        )
        
        # تحديث معلومات المستخدم إذا كان موجوداً
        if not created:
            if not user.first_name and given_name:
                user.first_name = given_name
            if not user.last_name and family_name:
                user.last_name = family_name
            if not user.is_email_verified:
                user.is_email_verified = True
            user.save()
        
        # تسجيل دخول المستخدم
        login(request, user)
        
        # تسجيل العملية
        logger.info(f"Google One Tap login successful for user: {email}")
        
        # تحديد الصفحة المراد التوجه إليها
        next_url = request.GET.get('next', '/')
        if user.user_type == 'barber':
            next_url = '/accounts/dashboard/barber/'
        else:
            next_url = '/barbershops/'
        
        return JsonResponse({
            'success': True,
            'message': f'مرحباً {user.first_name or user.username}!',
            'redirect_url': next_url,
            'user_created': created
        })
        
    except ValueError as e:
        logger.error(f"Google token verification failed: {e}")
        return JsonResponse({
            'success': False, 
            'error': 'Invalid token'
        })
    except Exception as e:
        logger.error(f"Google One Tap login error: {e}")
        return JsonResponse({
            'success': False, 
            'error': 'Login failed'
        })

def google_login_status(request):
    """
    فحص حالة تسجيل الدخول عبر Google
    """
    if request.user.is_authenticated:
        return JsonResponse({
            'authenticated': True,
            'user': {
                'email': request.user.email,
                'name': request.user.get_full_name(),
                'user_type': request.user.user_type,
            }
        })
    else:
        return JsonResponse({
            'authenticated': False
        })

def google_logout(request):
    """
    تسجيل خروج من Google
    """
    from django.contrib.auth import logout
    logout(request)
    messages.success(request, 'تم تسجيل الخروج بنجاح')
    return redirect('home:index')

class GoogleOAuthMixin:
    """
    Mixin لإضافة معلومات Google OAuth إلى القوالب
    """
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        
        # إضافة Google Client ID للقوالب
        context['GOOGLE_CLIENT_ID'] = getattr(settings, 'GOOGLE_ONE_TAP_CLIENT_ID', '')
        context['GOOGLE_AUTH_AVAILABLE'] = GOOGLE_AUTH_AVAILABLE
        
        return context