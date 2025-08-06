#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Context processors للحسابات
"""
from django.conf import settings

def google_oauth_context(request):
    """
    إضافة معلومات Google OAuth إلى جميع القوالب
    """
    return {
        'GOOGLE_CLIENT_ID': getattr(settings, 'GOOGLE_ONE_TAP_CLIENT_ID', ''),
        'GOOGLE_AUTH_AVAILABLE': True,
    }