from django.contrib import admin
from django.utils.html import format_html
from .models import Booking, BookingHistory, BookingMessage


@admin.register(Booking)
class BookingAdmin(admin.ModelAdmin):
    list_display = [
        'id', 'customer_display', 'barbershop_name', 'service_name', 
        'booking_day', 'queue_number', 'status_badge', 'total_price', 'created_at'
    ]
    list_filter = ['status', 'booking_day', 'created_at', 'barbershop']
    search_fields = [
        'customer__username', 'customer__email', 'customer_name',
        'barbershop__name', 'service__name'
    ]
    readonly_fields = ['created_at', 'updated_at']
    date_hierarchy = 'booking_day'
    
    fieldsets = (
        ('معلومات الحجز', {
            'fields': ('customer', 'customer_name', 'customer_phone', 'customer_email')
        }),
        ('تفاصيل الخدمة', {
            'fields': ('barbershop', 'service', 'booking_day', 'queue_number')
        }),
        ('التفاصيل المالية', {
            'fields': ('total_price',)
        }),
        ('الحالة والملاحظات', {
            'fields': ('status', 'notes')
        }),
        ('التواريخ', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )
    
    def customer_display(self, obj):
        if obj.customer:
            return obj.customer.get_full_name() or obj.customer.username
        return obj.customer_name or 'غير محدد'
    customer_display.short_description = 'العميل'
    
    def barbershop_name(self, obj):
        return obj.barbershop.name
    barbershop_name.short_description = 'صالون الحلاقة'
    
    def service_name(self, obj):
        return obj.service.name
    service_name.short_description = 'الخدمة'
    
    def status_badge(self, obj):
        colors = {
            'pending': 'warning',
            'confirmed': 'info',
            'completed': 'success',
            'cancelled': 'danger',
            'no_show': 'secondary'
        }
        color = colors.get(obj.status, 'secondary')
        return format_html(
            '<span class="badge bg-{}">{}</span>',
            color,
            obj.get_status_display()
        )
    status_badge.short_description = 'الحالة'
    
    def get_queryset(self, request):
        return super().get_queryset(request).select_related(
            'customer', 'barbershop', 'service'
        )


@admin.register(BookingHistory)
class BookingHistoryAdmin(admin.ModelAdmin):
    list_display = ['booking', 'old_status', 'new_status', 'changed_by', 'created_at']
    list_filter = ['old_status', 'new_status', 'created_at']
    search_fields = ['booking__customer__username', 'booking__barbershop__name', 'changed_by__username']
    readonly_fields = ['created_at']
    
    def get_queryset(self, request):
        return super().get_queryset(request).select_related(
            'booking', 'booking__customer', 'booking__barbershop', 'changed_by'
        )


@admin.register(BookingMessage)
class BookingMessageAdmin(admin.ModelAdmin):
    list_display = ['booking', 'sender', 'message_preview', 'is_read', 'created_at']
    list_filter = ['is_read', 'created_at']
    search_fields = ['booking__customer__username', 'sender__username', 'message']
    readonly_fields = ['created_at']
    
    def message_preview(self, obj):
        return obj.message[:50] + '...' if len(obj.message) > 50 else obj.message
    message_preview.short_description = 'معاينة الرسالة'
    
    def get_queryset(self, request):
        return super().get_queryset(request).select_related(
            'booking', 'booking__customer', 'sender'
        )


# تخصيص عنوان لوحة التحكم
admin.site.site_header = "لوحة تحكم Barber Shop"
admin.site.site_title = "إدارة الموقع"
admin.site.index_title = "مرحباً بك في لوحة التحكم"