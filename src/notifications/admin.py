from django.contrib import admin
from .models import Notification


@admin.register(Notification)
class NotificationAdmin(admin.ModelAdmin):
    list_display = ['title', 'recipient', 'notification_type', 'is_read', 'created_at']
    list_filter = ['notification_type', 'is_read', 'created_at']
    search_fields = ['title', 'message', 'recipient__username', 'recipient__email']
    readonly_fields = ['created_at']
    list_per_page = 25
    
    fieldsets = (
        ('معلومات الإشعار', {
            'fields': ('recipient', 'sender', 'notification_type', 'title', 'message')
        }),
        ('معلومات إضافية', {
            'fields': ('booking', 'is_read', 'created_at')
        }),
    )
    
    def get_queryset(self, request):
        return super().get_queryset(request).select_related('recipient', 'sender', 'booking')