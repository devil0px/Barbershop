"""
Custom adapter لحل مشكلة MultipleObjectsReturned في Google OAuth
"""
from allauth.socialaccount.adapter import DefaultSocialAccountAdapter
from allauth.socialaccount.models import SocialApp
from django.contrib.sites.models import Site
from django.contrib.auth import get_user_model
from django.http import HttpResponseRedirect
from django.urls import reverse

class CustomSocialAccountAdapter(DefaultSocialAccountAdapter):
    
    def get_app(self, request, provider, config=None):
        """
        حل مشكلة MultipleObjectsReturned عند وجود تطبيقات متعددة لنفس الـ provider
        """
        # تحديد الموقع الحالي
        current_site = self.get_current_site(request)
        
        try:
            # البحث عن تطبيق مرتبط بالموقع الحالي فقط
            app = SocialApp.objects.get(
                provider=provider,
                sites=current_site
            )
            return app
        except SocialApp.DoesNotExist:
            # إذا لم يوجد تطبيق للموقع الحالي، استخدم أي تطبيق متاح
            try:
                apps = SocialApp.objects.filter(provider=provider)
                if apps.exists():
                    return apps.first()
                else:
                    raise SocialApp.DoesNotExist(f"No SocialApp found for provider '{provider}'")
            except Exception:
                raise SocialApp.DoesNotExist(f"No SocialApp found for provider '{provider}'")
        except SocialApp.MultipleObjectsReturned:
            # إذا لا يزال هناك تطبيقات متعددة للموقع الحالي، استخدم الأول
            apps = SocialApp.objects.filter(
                provider=provider,
                sites=current_site
            )
            return apps.first()
    
    def get_current_site(self, request):
        """
        الحصول على الموقع الحالي حسب النطاق
        """
        # فحص وجود request لتجنب خطأ NoneType
        if request is None:
            # إرجاع الموقع الافتراضي إذا لم يكن request متاح
            try:
                return Site.objects.get(domain='localhost:8000')
            except Site.DoesNotExist:
                return Site.objects.create(
                    domain='localhost:8000',
                    name='Localhost Development'
                )
        
        host = request.get_host()
        
        # تحديث للنطاق الجديد
        if '15d0212cf8fe.ngrok-free.app' in host:
            try:
                return Site.objects.get(domain='15d0212cf8fe.ngrok-free.app')
            except Site.DoesNotExist:
                # إنشاء الموقع إذا لم يكن موجوداً
                return Site.objects.create(
                    domain='15d0212cf8fe.ngrok-free.app',
                    name='Ngrok Site'
                )
        else:
            try:
                return Site.objects.get(domain='localhost:8000')
            except Site.DoesNotExist:
                # إنشاء الموقع إذا لم يكن موجوداً
                return Site.objects.create(
                    domain='localhost:8000',
                    name='Localhost Development'
                )

    def populate_user(self, request, sociallogin, data):
        """
        ملء بيانات المستخدم من Google OAuth
        """
        user = super().populate_user(request, sociallogin, data)
        
        # استخراج معلومات إضافية من Google
        if sociallogin.account.provider == 'google':
            extra_data = sociallogin.account.extra_data
            
            # تحديث الاسم الأول والأخير
            if not user.first_name and extra_data.get('given_name'):
                user.first_name = extra_data.get('given_name', '')
            if not user.last_name and extra_data.get('family_name'):
                user.last_name = extra_data.get('family_name', '')
            
            # تحديث اسم المستخدم إذا لم يكن موجوداً
            if not user.username:
                username = extra_data.get('name', '').lower().replace(' ', '')
                if not username:
                    username = user.email.split('@')[0] if user.email else 'user'
                
                # التأكد من أن اسم المستخدم فريد
                original_username = username
                counter = 1
                User = get_user_model()
                while User.objects.filter(username=username).exists():
                    username = f"{original_username}{counter}"
                    counter += 1
                
                user.username = username
            
            # تفعيل الإيميل تلقائياً لحسابات Google
            user.is_email_verified = True
            user.is_active = True
            
        return user
    
    def save_user(self, request, sociallogin, form=None):
        """
        حفظ المستخدم الجديد من Google OAuth
        """
        user = super().save_user(request, sociallogin, form)
        return user
    
    def is_auto_signup_allowed(self, request, sociallogin):
        """
        السماح بالتسجيل التلقائي
        """
        return True
    
    def pre_social_login(self, request, sociallogin):
        """
        ربط الحسابات تلقائياً عند وجود نفس الإيميل
        """
        # إذا لم يكن هناك مستخدم مسجل دخول بالفعل
        if sociallogin.is_existing:
            return
            
        if sociallogin.account.provider == 'google':
            try:
                # البحث عن مستخدم بنفس الإيميل
                User = get_user_model()
                email = sociallogin.account.extra_data.get('email')
                if email:
                    existing_user = User.objects.get(email__iexact=email)
                    # ربط الحساب الاجتماعي بالمستخدم الموجود
                    sociallogin.connect(request, existing_user)
            except User.DoesNotExist:
                # لا يوجد مستخدم بهذا الإيميل - متابعة عادية
                pass
    
    def get_signup_form_initial_data(self, sociallogin):
        """
        البيانات الأولية لنموذج التسجيل
        """
        initial = {}
        
        if sociallogin.account.provider == 'google':
            extra_data = sociallogin.account.extra_data
            initial.update({
                'first_name': extra_data.get('given_name', ''),
                'last_name': extra_data.get('family_name', ''),
                'email': extra_data.get('email', ''),
            })
        return initial