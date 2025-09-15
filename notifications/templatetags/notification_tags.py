from django import template
from django.utils.safestring import mark_safe
from notifications.models import Notification

register = template.Library()


@register.simple_tag
def unread_notifications_count(user):
    """إرجاع عدد الإشعارات غير المقروءة للمستخدم"""
    if user.is_authenticated:
        return Notification.objects.filter(recipient=user, is_read=False).count()
    return 0


@register.inclusion_tag('notifications/notification_badge.html')
def notification_badge(user):
    """عرض شارة الإشعارات"""
    if user.is_authenticated:
        count = Notification.objects.filter(recipient=user, is_read=False).count()
        return {'count': count}
    return {'count': 0}


@register.inclusion_tag('notifications/recent_notifications.html')
def recent_notifications(user, limit=5):
    """عرض آخر الإشعارات"""
    if user.is_authenticated:
        notifications = Notification.objects.filter(
            recipient=user
        ).order_by('-created_at')[:limit]
        return {'notifications': notifications}
    return {'notifications': []}


@register.filter
def notification_icon(notification_type):
    """إرجاع أيقونة الإشعار حسب النوع"""
    icons = {
        'new_message': 'fas fa-comment',
        'booking_confirmed': 'fas fa-check-circle',
        'booking_cancelled': 'fas fa-times-circle',
        'booking_completed': 'fas fa-star',
        'new_booking': 'fas fa-calendar-plus',
        'turn_updated': 'fas fa-clock',
    }
    return icons.get(notification_type, 'fas fa-bell')


@register.filter
def notification_color(notification_type):
    """إرجاع لون الإشعار حسب النوع"""
    colors = {
        'new_message': 'text-primary',
        'booking_confirmed': 'text-success',
        'booking_cancelled': 'text-danger',
        'booking_completed': 'text-info',
        'new_booking': 'text-warning',
        'turn_updated': 'text-secondary',
    }
    return colors.get(notification_type, 'text-dark')


@register.simple_tag
def notification_title(notification_type):
    """إرجاع عنوان الإشعار حسب ��لنوع"""
    titles = {
        'new_message': 'رسالة جديدة',
        'booking_confirmed': 'تم تأكيد الحجز',
        'booking_cancelled': 'تم إلغاء الحجز',
        'booking_completed': 'تم إنجاز الحجز',
        'new_booking': 'حجز جديد',
        'turn_updated': 'تم تحديث الدور',
    }
    return titles.get(notification_type, 'إشعار')