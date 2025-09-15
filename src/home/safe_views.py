from django.shortcuts import render
from django.http import HttpResponse
from django.views.generic import TemplateView
from django.db import connection

class SafeHomePageView(TemplateView):
    """صفحة رئيسية آمنة تتعامل مع الأخطاء"""
    template_name = 'index.html'
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        
        try:
            # محاولة تحميل النماذج
            from .models import SiteSettings, HomePageFeature, Testimonial
            from barbershops.models import Barbershop
            from reviews.models import Review
            
            # إعدادات الموقع
            try:
                context['site_settings'] = SiteSettings.get_settings()
            except:
                # إنشاء إعدادات افتراضية
                context['site_settings'] = type('obj', (object,), {
                    'site_name': 'Barber Shop',
                    'hero_title': 'أفضل صالون حلاقة في المدينة',
                    'hero_subtitle': 'منذ عام 1973، نقدم خدمات حلاقة عالية الجودة',
                    'about_title': 'خبرة تمتد لأكثر من 50 عاماً',
                    'about_description': 'نحن نقدم أفضل خدمات الحلاقة في المدينة',
                    'phone_number': '+20109841514',
                    'email': 'devil0px@gmail.com',
                    'address': 'مدينتي - اسم الشارع',
                    'working_hours': 'يومياً من 8:00 ص إلى 10:00 م',
                    'facebook_url': '',
                    'instagram_url': '',
                    'twitter_url': '',
                    'whatsapp_number': '',
                })
            
            # الصالونات
            try:
                context['barbershops'] = Barbershop.objects.filter(
                    is_active=True, is_verified=True
                )[:6]
            except:
                context['barbershops'] = []
            
            # الميزات
            try:
                context['features'] = HomePageFeature.objects.filter(is_active=True)[:4]
            except:
                context['features'] = []
            
            # الشهادات
            try:
                context['testimonials'] = Testimonial.objects.filter(is_active=True)[:6]
            except:
                context['testimonials'] = []
            
            # التقييمات
            try:
                context['reviews'] = Review.objects.filter(is_approved=True)[:5]
            except:
                context['reviews'] = []
                
        except Exception as e:
            # في حالة فشل تحميل النماذج، استخدم البيانات الافتراضية
            context['site_settings'] = type('obj', (object,), {
                'site_name': 'Barber Shop',
                'hero_title': 'أفضل صالون حلاقة في المدينة',
                'hero_subtitle': 'منذ عام 1973، نقدم خدمات حلاقة عالية الجودة',
                'about_title': 'خبرة تمتد لأكثر من 50 عاماً',
                'about_description': 'نحن نقدم أفضل خدمات الحلاقة في المدينة',
                'phone_number': '+20109841514',
                'email': 'devil0px@gmail.com',
                'address': 'مدينتي - اسم الشارع',
                'working_hours': 'يومياً من 8:00 ص إلى 10:00 م',
            })
            context['barbershops'] = []
            context['features'] = []
            context['testimonials'] = []
            context['reviews'] = []
            context['error_message'] = f'تحذير: {str(e)}'
        
        return context