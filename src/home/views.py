from django.shortcuts import render
from django.views.generic import ListView
from django.db.models import Avg
from barbershops.models import Barbershop
from reviews.models import Review
from .models import SiteSettings, HomePageFeature, Testimonial, HeroSlide


class HomePageView(ListView):
    model = Barbershop
    template_name = 'index.html'
    context_object_name = 'barbershops'

    def get_queryset(self):
        # ترتيب الصالونات حسب متوسط التقييمات ثم حسب تاريخ الإنشاء
        return Barbershop.objects.filter(
            is_active=True, 
            is_verified=True
        ).annotate(
            avg_rating=Avg('reviews__rating')
        ).order_by('-avg_rating', '-created_at')[:6]

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        
        # إعدادات الموقع
        context['site_settings'] = SiteSettings.get_settings()
        
        # ميزات الصفحة الرئيسية
        context['features'] = HomePageFeature.objects.filter(is_active=True).order_by('order')
        
        # شهادات العملاء
        context['testimonials'] = Testimonial.objects.filter(is_active=True).order_by('-is_featured', 'order')[:6]
        
        # شرائح البانر
        context['hero_slides'] = HeroSlide.objects.filter(is_active=True).order_by('order')
        
        # التقييمات (للعرض في قسم آراء العملاء)
        context['reviews'] = Review.objects.filter(is_approved=True).order_by('-created_at')[:5]
        
        return context