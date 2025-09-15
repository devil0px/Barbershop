from django.db.models.signals import post_save
from django.dispatch import receiver
from bookings.models import BookingMessage, Booking
from .utils import create_chat_notification, create_booking_notification


@receiver(post_save, sender=BookingMessage)
def create_message_notification(sender, instance, created, **kwargs):
    """
    إنشاء إشعار عند إرسال رسالة جديدة في المحادثة
    """
    if created:  # فقط عند إنشاء رسالة جديدة
        create_chat_notification(instance)


@receiver(post_save, sender=Booking)
def create_booking_notifications(sender, instance, created, **kwargs):
    """
    إنشاء إشعارات عند إنشاء أو تحديث الحجز
    """
    if created:
        # إشعار صاحب المحل بحجز جديد
        create_booking_notification(instance, 'new_booking')
    else:
        # التحقق من تغيير الحالة
        if hasattr(instance, '_state') and instance._state.adding is False:
            # الحصول على الحالة السابقة من قاعدة البيانات
            try:
                old_booking = Booking.objects.get(pk=instance.pk)
                if old_booking.status != instance.status:
                    # تم تغيير الحالة، إنشاء إشعار مناسب
                    if instance.status == 'confirmed':
                        create_booking_notification(instance, 'booking_confirmed')
                    elif instance.status == 'cancelled':
                        create_booking_notification(instance, 'booking_cancelled')
                    elif instance.status == 'completed':
                        create_booking_notification(instance, 'booking_completed')
            except Booking.DoesNotExist:
                pass