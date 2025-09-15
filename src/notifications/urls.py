from django.urls import path
from . import views

app_name = 'notifications'

urlpatterns = [
    path('', views.NotificationListView.as_view(), name='list'),
    path('mark-read/<int:notification_id>/', views.mark_notification_read, name='mark_read'),
    path('mark-all-read/', views.mark_all_read, name='mark_all_read'),
    path('api/unread-count/', views.get_unread_count, name='unread_count'),
    path('api/recent/', views.get_recent_notifications, name='recent'),
]