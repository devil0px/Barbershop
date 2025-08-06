from django.shortcuts import render
from django.http import HttpResponseNotFound, HttpResponseServerError
import logging

logger = logging.getLogger(__name__)

def custom_404_view(request, exception=None):
    """
    صفحة 404 مخصصة آمنة بدون كشف معلومات حساسة
    """
    # تسجيل محاولة الوصول للصفحة غير الموجودة (للمراقبة الأمنية)
    user = getattr(request, 'user', 'Unknown')
    logger.warning(f"404 Error: User {user} tried to access {request.path}")
    
    return render(request, '404.html', status=404)

def custom_500_view(request):
    """
    صفحة 500 مخصصة آمنة بدون كشف معلومات حساسة
    """
    # تسجيل الخطأ الداخلي (للمراقبة الأمنية)
    user = getattr(request, 'user', 'Unknown')
    logger.error(f"500 Error: Internal server error for user {user} at {request.path}")
    
    return render(request, '500.html', status=500)

def custom_403_view(request, exception=None):
    """
    صفحة 403 مخصصة آمنة بدون كشف معلومات حساسة
    """
    # تسجيل محاولة الوصول غير المصرح بها (للمراقبة الأمنية)
    user = getattr(request, 'user', 'Unknown')
    logger.warning(f"403 Error: User {user} tried to access forbidden resource {request.path}")
    
    return render(request, '403.html', status=403)
