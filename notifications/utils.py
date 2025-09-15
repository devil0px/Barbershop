from .models import Notification
from django.contrib.auth import get_user_model

User = get_user_model()


def create_notification(recipient, notification_type, title, message, sender=None, booking=None):
    """
    إنشاء إشعار جديد
    
    Args:
        recipient: المستخدم المستلم للإشعار
        notification_type: نوع الإشعار
        title: عنوان الإشعار
        message: نص الإشعار
        sender: المرسل (اختياري)
        booking: الحجز المرتبط (اختياري)
    
    Returns:
        Notification: الإشعار المُنشأ
    """
    return Notification.objects.create(
        recipient=recipient,
        sender=sender,
        notification_type=notification_type,
        title=title,
        message=message,
        booking=booking
    )


def create_chat_notification(message_obj):
    """
    إنشاء إشعار لرسالة محادثة جديدة
    
    Args:
        message_obj: كائن BookingMessage
    """
    booking = message_obj.booking
    sender = message_obj.sender
    
    # تحديد المستلم (الطرف الآخر في المحادثة)
    if sender == booking.customer:
        # إذا كان المرسل هو العميل، فالمستلم هو صاحب المحل
        recipient = booking.barbershop.owner
        title = f"رسالة جديدة من {sender.get_full_name() or sender.username}"
    else:
        # إذا كان المرسل هو صاحب المحل، فالمستلم هو العميل
        recipient = booking.customer
        title = f"رسالة جديدة من {booking.barbershop.name}"
    
    # إنشاء الإشعار فقط إذا كان هناك مستلم
    if recipient:
        return create_notification(
            recipient=recipient,
            sender=sender,
            notification_type='new_message',
            title=title,
            message=f"حجز #{booking.id}: {message_obj.message[:100]}...",
            booking=booking
        )
    
    return None


def create_booking_notification(booking, notification_type, custom_message=None):
    """
    إنشاء إشعار متعلق بالحجز
    
    Args:
        booking: كائن Booking
        notification_type: نوع الإشعار
        custom_message: رسالة مخصصة (اختياري)
    """
    # تحديد العنوان والرسالة حسب نوع الإشعار
    titles = {
        'new_booking': 'حجز جديد',
        'booking_confirmed': 'تم تأكيد الحجز',
        'booking_cancelled': 'تم إلغاء الحجز',
        'booking_completed': 'تم إنجاز الحجز',
        'turn_updated': 'تم تحديث الدور',
    }
    
    # حساب قائمة الخدمات للحجز متعدد الخدمات
    booking_services = booking.booking_services.all()
    if booking_services.exists():
        services_names = []
        for bs in booking_services:
            if bs.service and hasattr(bs.service, 'name') and bs.service.name:
                services_names.append(bs.service.name)
        
        if services_names:
            if len(services_names) == 1:
                services_text = f"للخدمة {services_names[0]}"
            else:
                services_text = f"للخدمات: {', '.join(services_names)}"
        else:
            services_text = "لخدمات مختارة"
    else:
        services_text = "لخدمات مختارة"
    
    messages = {
        'new_booking': f'حجز جديد في {booking.barbershop.name} {services_text}',
        'booking_confirmed': f'تم تأكيد حجزك في {booking.barbershop.name}',
        'booking_cancelled': f'تم إلغاء حجزك في {booking.barbershop.name}',
        'booking_completed': f'تم إنجاز حجزك في {booking.barbershop.name}',
        'turn_updated': f'تم تحديث دورك في {booking.barbershop.name}',
    }
    
    title = titles.get(notification_type, 'إشعار حجز')
    message = custom_message or messages.get(notification_type, 'تحديث على حجزك')
    
    # تحديد المستلم والمرسل
    if notification_type == 'new_booking':
        # إشعار صاحب المحل بحجز جديد
        recipient = booking.barbershop.owner
        sender = booking.customer
    else:
        # إشعار العميل بتحديث الحجز
        recipient = booking.customer
        sender = booking.barbershop.owner
    
    if recipient:
        return create_notification(
            recipient=recipient,
            sender=sender,
            notification_type=notification_type,
            title=title,
            message=message,
            booking=booking
        )
    
    return None


def mark_booking_messages_as_read(booking, user):
    """
    تحديد رسائل الحجز كمقروءة للمستخدم المحدد
    
    Args:
        booking: كائن Booking
        user: المستخدم الذي قرأ الرسائل
    """
    # تحديد الرسائل غير المقروءة من الطرف الآخر
    unread_messages = booking.messages.filter(
        is_read=False
    ).exclude(sender=user)
    
    # تحديثها كمقروءة
    unread_messages.update(is_read=True)
    
    # تحديد الإشعارات المرتبطة كمقروءة أيضاً
    Notification.objects.filter(
        recipient=user,
        booking=booking,
        notification_type='new_message',
        is_read=False
    ).update(is_read=True)