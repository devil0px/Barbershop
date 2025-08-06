"""
Middleware مخصص لحل مشاكل Django Sites مع ngrok وتسجيل أخطاء Allauth
"""
import logging
from django.conf import settings
from django.contrib.sites.models import Site
from django.http import HttpResponseRedirect
from django.urls import reverse


class DynamicSiteMiddleware:
    """
    Middleware لتحديد SITE_ID ديناميكياً حسب النطاق
    """
    
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        # تحديد الموقع الحالي حسب النطاق
        host = request.get_host()
        
        if 'bff867bb20c4.ngrok-free.app' in host:
            # ngrok domain
            try:
                site = Site.objects.get(domain='bff867bb20c4.ngrok-free.app')
                settings.SITE_ID = site.id
            except Site.DoesNotExist:
                # إنشاء الموقع إذا لم يكن موجوداً
                site = Site.objects.create(
                    domain='bff867bb20c4.ngrok-free.app',
                    name='Ngrok Site'
                )
                settings.SITE_ID = site.id
        else:
            # localhost domain
            try:
                site = Site.objects.get(domain='localhost:8000')
                settings.SITE_ID = site.id
            except Site.DoesNotExist:
                # إنشاء الموقع إذا لم يكن موجوداً
                site = Site.objects.create(
                    domain='localhost:8000',
                    name='Localhost Development'
                )
                settings.SITE_ID = site.id
        
        # إضافة الموقع الحالي إلى request
        request.current_site = site
        
        response = self.get_response(request)
        return response


class SocialAuthDebugMiddleware:
    """
    Middleware لتسجيل أخطاء Django Allauth التفصيلية
    """
    
    def __init__(self, get_response):
        self.get_response = get_response
        self.logger = logging.getLogger('socialauth')
    
    def __call__(self, request):
        # تسجيل معلومات الطلب
        if '/accounts/google/' in request.path:
            self.logger.info(f"Google OAuth request: {request.method} {request.path}")
            self.logger.info(f"Host: {request.get_host()}")
            # فحص وجود user attribute قبل الوصول إليه
            user_info = getattr(request, 'user', 'Not available yet')
            self.logger.info(f"User: {user_info}")
        
        response = self.get_response(request)
        
        # تسجيل معلومات الاستجابة
        if '/accounts/google/' in request.path:
            self.logger.info(f"Response status: {response.status_code}")
            if hasattr(response, 'url'):
                self.logger.info(f"Redirect to: {response.url}")
        
        return response
    
    def process_exception(self, request, exception):
        """تسجيل الأخطاء التفصيلية"""
        if '/accounts/' in request.path:
            self.logger.error(f"Social auth error: {exception}")
            self.logger.error(f"Request path: {request.path}")
            self.logger.error(f"Request method: {request.method}")
            self.logger.error(f"Request host: {request.get_host()}")
            # فحص وجود user attribute قبل الوصول إليه
            user_info = getattr(request, 'user', 'Not available yet')
            self.logger.error(f"User: {user_info}")
            
            # معلومات إضافية للتشخيص
            if hasattr(request, 'session'):
                self.logger.error(f"Session keys: {list(request.session.keys())}")
            
            import traceback
            self.logger.error(f"Traceback: {traceback.format_exc()}")
        
        return None  # السماح للمعالج الافتراضي بالتعامل مع الخطأ


class AdminSecurityMiddleware:
    """
    Middleware لحماية صفحة الإدارة من الوصول غير المصرح به
    """
    
    def __init__(self, get_response):
        self.get_response = get_response
        self.logger = logging.getLogger('security')
    
    def __call__(self, request):
        # فحص محاولات الوصول لصفحة الإدارة القديمة
        if request.path.startswith('/admin/'):
            # تسجيل محاولة الوصول المشبوهة
            user = getattr(request, 'user', 'Unknown')
            self.logger.warning(
                f"Suspicious admin access attempt from IP: {self.get_client_ip(request)} "
                f"User: {user} Path: {request.path} User-Agent: {request.META.get('HTTP_USER_AGENT', 'Unknown')}"
            )
            # إعادة توجيه إلى صفحة 404 مخصصة
            from django.http import Http404
            raise Http404("Page not found")
        
        # فحص محاولات الوصول لصفحة الإدارة الجديدة
        if request.path.startswith('/secure-admin-panel-2024/'):
            # تسجيل محاولة الوصول
            user = getattr(request, 'user', 'Unknown')
            self.logger.info(
                f"Admin access attempt from IP: {self.get_client_ip(request)} "
                f"User: {user} Path: {request.path}"
            )
            
            # يمكن إضافة فحوصات إضافية هنا مثل:
            # - فحص IP المسموح
            # - فحص الوقت المسموح
            # - فحص عدد المحاولات
        
        response = self.get_response(request)
        return response
    
    def get_client_ip(self, request):
        """الحصول على IP الحقيقي للعميل"""
        x_forwarded_for = request.META.get('HTTP_X_FORWARDED_FOR')
        if x_forwarded_for:
            ip = x_forwarded_for.split(',')[0]
        else:
            ip = request.META.get('REMOTE_ADDR')
        return ip