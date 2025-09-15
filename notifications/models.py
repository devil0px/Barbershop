from django.db import models
from django.contrib.auth import get_user_model
from bookings.models import Booking

User = get_user_model()

class Notification(models.Model):
    NOTIFICATION_TYPES = (
        ('new_message', 'رسالة جديدة'),
        ('booking_confirmed', 'تم تأكيد الحجز'),
        ('booking_cancelled', 'تم إلغاء الحجز'),
        ('booking_completed', 'تم إنجاز الحجز'),
        ('new_booking', 'حجز جديد'),
        ('turn_updated', 'تم تحديث الدور'),
    )

    recipient = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='notifications',
        verbose_name='المستلم'
    )
    sender = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='sent_notifications',
        verbose_name='المرسل',
        null=True,
        blank=True
    )
    notification_type = models.CharField(
        max_length=20,
        choices=NOTIFICATION_TYPES,
        verbose_name='نوع الإشعار'
    )
    title = models.CharField(
        max_length=200,
        verbose_name='العنوان'
    )
    message = models.TextField(
        verbose_name='الرسالة'
    )
    booking = models.ForeignKey(
        Booking,
        on_delete=models.CASCADE,
        related_name='notifications',
        verbose_name='الحجز',
        null=True,
        blank=True
    )
    is_read = models.BooleanField(
        default=False,
        verbose_name='تم قراءتها'
    )
    created_at = models.DateTimeField(
        auto_now_add=True,
        verbose_name='تاريخ الإنشاء'
    )

    class Meta:
        verbose_name = 'إشعار'
        verbose_name_plural = 'الإشعارات'
        ordering = ['-created_at']

    def __str__(self):
        return f"{self.title} - {self.recipient.username}"

    def mark_as_read(self):
        """تحديد الإشعار كمقروء"""
        self.is_read = True
        self.save(update_fields=['is_read'])

    def get_icon(self):
        """إرجاع أيقونة الإشعار"""
        icons = {
            'new_message': 'fas fa-comment',
            'booking_confirmed': 'fas fa-check-circle',
            'booking_cancelled': 'fas fa-times-circle',
            'booking_completed': 'fas fa-star',
            'new_booking': 'fas fa-calendar-plus',
            'turn_updated': 'fas fa-clock',
        }
        return icons.get(self.notification_type, 'fas fa-bell')

    def get_color_class(self):
        """إرجاع لون الإشعار"""
        colors = {
            'new_message': 'text-primary',
            'booking_confirmed': 'text-success',
            'booking_cancelled': 'text-danger',
            'booking_completed': 'text-info',
            'new_booking': 'text-warning',
            'turn_updated': 'text-secondary',
        }
        return colors.get(self.notification_type, 'text-dark')