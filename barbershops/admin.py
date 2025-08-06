from django.contrib import admin
from .models import Barbershop, BarbershopImage, Service, ServiceImage

class BarbershopImageInline(admin.TabularInline):
    model = BarbershopImage
    extra = 1

class ServiceInline(admin.TabularInline):
    model = Service
    extra = 1
    fields = ['name', 'price', 'duration', 'is_active']

@admin.register(Barbershop)
class BarbershopAdmin(admin.ModelAdmin):
    list_display = ['name', 'owner', 'phone_number', 'is_active', 'is_verified', 'created_at']
    list_filter = ['is_active', 'is_verified', 'created_at']
    search_fields = ['name', 'owner__username', 'phone_number']
    readonly_fields = ['created_at', 'updated_at']
    inlines = [BarbershopImageInline, ServiceInline]
    
    fieldsets = (
        ('معلومات أساسية', {
            'fields': ('owner', 'name', 'description', 'address', 'phone_number', 'email')
        }),
        ('الموقع', {
            'fields': ('latitude', 'longitude')
        }),
        ('أوقات العمل', {
            'fields': ('opening_time', 'closing_time')
        }),
        ('الصورة', {
            'fields': ('image',)
        }),
        ('الحالة', {
            'fields': ('is_active', 'is_verified')
        }),
        ('إعدادات متقدمة', {
            'fields': ('is_premium', 'premium_until', 'theme_color', 'whatsapp_number', 'instagram_username'),
            'classes': ('collapse',)
        }),
        ('إعدادات الحجز', {
            'fields': ('allow_online_booking', 'minimum_booking_time', 'maximum_booking_time', 'booking_advance_days'),
            'classes': ('collapse',)
        }),
        ('إعدادات الإشعارات', {
            'fields': ('notify_by_email', 'notify_by_sms', 'notify_by_whatsapp'),
            'classes': ('collapse',)
        }),
        ('التواريخ', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )

class ServiceImageInline(admin.TabularInline):
    model = ServiceImage
    extra = 1

@admin.register(Service)
class ServiceAdmin(admin.ModelAdmin):
    list_display = ['name', 'barbershop', 'category', 'price', 'duration', 'is_active', 'created_at']
    list_filter = ['category', 'is_active', 'created_at', 'barbershop']
    search_fields = ['name', 'barbershop__name']
    readonly_fields = ['created_at']
    inlines = [ServiceImageInline]
    
    fieldsets = (
        ('معلومات أساسية', {
            'fields': ('barbershop', 'name', 'description', 'category')
        }),
        ('التسعير والوقت', {
            'fields': ('price', 'duration')
        }),
        ('الصورة', {
            'fields': ('image',)
        }),
        ('إعدادات الخدمة', {
            'fields': ('is_popular', 'popularity_score', 'is_active'),
            'classes': ('collapse',)
        }),
        ('إعدادات متقدمة', {
            'fields': ('required_tools', 'preparation_time', 'min_booking_time', 'max_booking_time', 'display_order'),
            'classes': ('collapse',)
        }),
        ('إحصائيات', {
            'fields': ('total_bookings', 'average_rating'),
            'classes': ('collapse',)
        }),
        ('التواريخ', {
            'fields': ('created_at',),
            'classes': ('collapse',)
        }),
    )

@admin.register(BarbershopImage)
class BarbershopImageAdmin(admin.ModelAdmin):
    list_display = ['barbershop', 'is_main', 'created_at']
    list_filter = ['is_main', 'created_at']
    search_fields = ['barbershop__name']

@admin.register(ServiceImage)
class ServiceImageAdmin(admin.ModelAdmin):
    list_display = ['service', 'created_at']
    list_filter = ['created_at']
    search_fields = ['service__name', 'service__barbershop__name']
