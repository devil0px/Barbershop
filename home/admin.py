from django.contrib import admin
from django.utils.html import format_html
from .models import SiteSettings, HomePageFeature, Testimonial, HeroSlide


@admin.register(SiteSettings)
class SiteSettingsAdmin(admin.ModelAdmin):
    list_display = ['site_name', 'updated_at']
    
    fieldsets = (
        ('معلومات الموقع الأساسية', {
            'fields': ('site_name', 'site_description', 'hero_title', 'hero_subtitle')
        }),
        ('قسم عنا', {
            'fields': ('about_title', 'about_description')
        }),
        ('الصور', {
            'fields': (
                ('about_image_1', 'about_image_1_alt'),
                ('about_image_2', 'about_image_2_alt'),
                ('about_image_3', 'about_image_3_alt'),
            ),
            'classes': ('collapse',)
        }),
        ('معلومات الاتصال', {
            'fields': ('phone_number', 'email', 'address', 'working_hours')
        }),
        ('روابط التواصل الاجتماعي', {
            'fields': ('facebook_url', 'instagram_url', 'twitter_url', 'whatsapp_number'),
            'classes': ('collapse',)
        }),
    )
    
    def has_add_permission(self, request):
        # السماح بإضافة سجل واحد فقط
        return not SiteSettings.objects.exists()
    
    def has_delete_permission(self, request, obj=None):
        # منع حذف إعدادات الموقع
        return False


@admin.register(HomePageFeature)
class HomePageFeatureAdmin(admin.ModelAdmin):
    list_display = ['title', 'icon_preview', 'order', 'is_active', 'updated_at']
    list_editable = ['order', 'is_active']
    list_filter = ['is_active', 'created_at']
    search_fields = ['title', 'description']
    ordering = ['order', 'id']
    
    fieldsets = (
        (None, {
            'fields': ('title', 'description', 'icon', 'order', 'is_active')
        }),
    )
    
    def icon_preview(self, obj):
        return format_html('<i class="{}"></i> {}', obj.icon, obj.icon)
    icon_preview.short_description = 'الأيقونة'


@admin.register(Testimonial)
class TestimonialAdmin(admin.ModelAdmin):
    list_display = ['customer_name', 'rating_stars', 'is_featured', 'is_active', 'order', 'created_at']
    list_editable = ['is_featured', 'is_active', 'order']
    list_filter = ['rating', 'is_featured', 'is_active', 'created_at']
    search_fields = ['customer_name', 'testimonial_text', 'position']
    ordering = ['-is_featured', 'order', '-created_at']
    
    fieldsets = (
        ('معلومات العميل', {
            'fields': ('customer_name', 'customer_image', 'position')
        }),
        ('الشهادة', {
            'fields': ('testimonial_text', 'rating')
        }),
        ('إعدادات العرض', {
            'fields': ('is_featured', 'is_active', 'order')
        }),
    )
    
    def rating_stars(self, obj):
        stars = '★' * obj.rating + '☆' * (5 - obj.rating)
        return format_html('<span style="color: #ffc107;">{}</span>', stars)
    rating_stars.short_description = 'التقييم'


@admin.register(HeroSlide)
class HeroSlideAdmin(admin.ModelAdmin):
    list_display = ['title', 'image_preview', 'button_text', 'is_active', 'order', 'updated_at']
    list_editable = ['is_active', 'order']
    list_filter = ['is_active', 'created_at']
    search_fields = ['title', 'subtitle']
    ordering = ['order', 'id']
    
    fieldsets = (
        ('محتوى الشريحة', {
            'fields': ('title', 'subtitle', 'background_image')
        }),
        ('إعدادات الزر', {
            'fields': ('button_text', 'button_url')
        }),
        ('إعدادات العرض', {
            'fields': ('is_active', 'order')
        }),
    )
    
    def image_preview(self, obj):
        if obj.background_image:
            return format_html(
                '<img src="{}" style="width: 50px; height: 30px; object-fit: cover; border-radius: 4px;" />',
                obj.background_image.url
            )
        return "لا توجد صورة"
    image_preview.short_description = 'معاينة الصورة'


# تخصيص عنوان لوحة التحكم
admin.site.site_header = "لوحة تحكم Barber Shop"
admin.site.site_title = "إدارة الموقع"
admin.site.index_title = "مرحباً بك في لوحة التحكم"