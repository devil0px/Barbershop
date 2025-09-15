from .models import Notification


def notifications_context(request):
    """
    إضافة معلومات الإشعارات لجميع الصفحات
    """
    if request.user.is_authenticated:
        unread_count = Notification.objects.filter(
            recipient=request.user,
            is_read=False
        ).count()
        
        recent_notifications = Notification.objects.filter(
            recipient=request.user
        ).order_by('-created_at')[:5]
        
        return {
            'notifications_unread_count': unread_count,
            'recent_notifications': recent_notifications,
        }
    
    return {
        'notifications_unread_count': 0,
        'recent_notifications': [],
    }