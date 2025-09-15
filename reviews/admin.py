from django.contrib import admin
from django.utils.html import format_html
from .models import Review


@admin.register(Review)
class ReviewAdmin(admin.ModelAdmin):
    list_display = [
        'id', 'customer_name', 'barbershop_name', 'rating_stars', 
        'is_approved', 'created_at'
    ]
    list_filter = ['rating', 'is_approved', 'created_at', 'barbershop']
    search_fields = [
        'customer__username', 'customer__email', 
        'barbershop__name', 'comment'
    ]
    readonly_fields = ['created_at', 'updated_at']
    date_hierarchy = 'created_at'
    
    fieldsets = (
        ('معلومات التقييم', {
            'fields': ('customer', 'barbershop', 'rating', 'comment')
        }),
        ('الحالة', {
            'fields': ('is_approved',)
        }),
        ('التواريخ', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )
    
    def customer_name(self, obj):
        return obj.customer.get_full_name() or obj.customer.username
    customer_name.short_description = 'العميل'
    
    def barbershop_name(self, obj):
        return obj.barbershop.name
    barbershop_name.short_description = 'صالون الحلاقة'
    
    def rating_stars(self, obj):
        stars = '★' * obj.rating + '☆' * (5 - obj.rating)
        return format_html('<span style="color: #ffc107;">{}</span>', stars)
    rating_stars.short_description = 'التقييم'
    
    def get_queryset(self, request):
        return super().get_queryset(request).select_related(
            'customer', 'barbershop'
        )
    
    actions = ['approve_reviews', 'disapprove_reviews']
    
    def approve_reviews(self, request, queryset):
        updated = queryset.update(is_approved=True)
        self.message_user(request, f'تم الموافقة على {updated} تقييم.')
    approve_reviews.short_description = 'الموافقة على التقييمات المحددة'
    
    def disapprove_reviews(self, request, queryset):
        updated = queryset.update(is_approved=False)
        self.message_user(request, f'تم رفض {updated} تقييم.')
    disapprove_reviews.short_description = 'رفض التقييمات ال��حددة'