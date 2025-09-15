from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from django.contrib.auth.mixins import LoginRequiredMixin
from django.views.generic import ListView
from django.http import JsonResponse
from django.views.decorators.http import require_POST
from django.views.decorators.csrf import csrf_exempt
from django.utils.decorators import method_decorator
from django.db.models import Q
from .models import Notification


class NotificationListView(LoginRequiredMixin, ListView):
    """عرض قائمة الإشعارات للمستخدم"""
    model = Notification
    template_name = 'notifications/list.html'
    context_object_name = 'notifications'
    paginate_by = 20

    def get_queryset(self):
        return Notification.objects.filter(
            recipient=self.request.user
        ).order_by('-created_at')

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['unread_count'] = Notification.objects.filter(
            recipient=self.request.user,
            is_read=False
        ).count()
        return context


@login_required
@require_POST
def mark_notification_read(request, notification_id):
    """تحديد إشعار كمقروء"""
    notification = get_object_or_404(
        Notification,
        id=notification_id,
        recipient=request.user
    )
    notification.mark_as_read()
    
    if request.headers.get('x-requested-with') == 'XMLHttpRequest':
        return JsonResponse({'status': 'success'})
    
    return redirect('notifications:list')


@login_required
@require_POST
def mark_all_read(request):
    """تحديد جميع الإشعارات كمقروءة"""
    Notification.objects.filter(
        recipient=request.user,
        is_read=False
    ).update(is_read=True)
    
    if request.headers.get('x-requested-with') == 'XMLHttpRequest':
        return JsonResponse({'status': 'success'})
    
    return redirect('notifications:list')


@login_required
def get_unread_count(request):
    """الحصول على عدد الإشعارات غير المقروءة"""
    count = Notification.objects.filter(
        recipient=request.user,
        is_read=False
    ).count()
    
    return JsonResponse({'unread_count': count})


@login_required
def get_recent_notifications(request):
    """الحصول على آخر الإشعارات"""
    notifications = Notification.objects.filter(
        recipient=request.user
    ).order_by('-created_at')[:5]
    
    notifications_data = []
    for notification in notifications:
        notifications_data.append({
            'id': notification.id,
            'title': notification.title,
            'message': notification.message,
            'type': notification.notification_type,
            'is_read': notification.is_read,
            'created_at': notification.created_at.strftime('%Y-%m-%d %H:%M'),
            'icon': notification.get_icon(),
            'color_class': notification.get_color_class(),
        })
    
    return JsonResponse({
        'notifications': notifications_data,
        'unread_count': Notification.objects.filter(
            recipient=request.user,
            is_read=False
        ).count()
    })