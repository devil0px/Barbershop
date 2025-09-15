from django.core.management.base import BaseCommand
from django.contrib.auth import get_user_model
from notifications.models import Notification
from bookings.models import Booking

User = get_user_model()


class Command(BaseCommand):
    help = 'إنشاء إشعارات تجريبية للاختبار'

    def add_arguments(self, parser):
        parser.add_argument(
            '--user-id',
            type=int,
            help='معرف المستخدم لإنشاء الإشعارات له',
        )
        parser.add_argument(
            '--count',
            type=int,
            default=5,
            help='عدد الإشعارات المراد إنشاؤها (افتراضي: 5)',
        )

    def handle(self, *args, **options):
        user_id = options.get('user_id')
        count = options.get('count')

        if user_id:
            try:
                user = User.objects.get(id=user_id)
            except User.DoesNotExist:
                self.stdout.write(
                    self.style.ERROR(f'المستخدم بالمعرف {user_id} غير موجود')
                )
                return
        else:
            # استخدام أول مستخدم متاح
            user = User.objects.first()
            if not user:
                self.stdout.write(
                    self.style.ERROR('لا يوجد مستخدمين في النظام')
                )
                return

        # إنشاء إشعارات تجريبية
        notification_types = [
            ('new_message', 'رسالة جديدة من العميل', 'لديك رسالة جديدة في المحادثة'),
            ('booking_confirmed', 'تم تأكيد حجزك', 'تم تأكيد حجزك بنجاح في صالون الحلاقة'),
            ('booking_cancelled', 'تم إلغاء الحجز', 'تم إلغاء حجزك من قبل صاحب المحل'),
            ('booking_completed', 'تم إنجاز الحجز', 'تم إنجاز خدمتك بنجاح'),
            ('new_booking', 'حجز جديد', 'لديك حجز جديد من عميل'),
            ('turn_updated', 'تحديث الدور', 'تم تحديث دورك في الط��بور'),
        ]

        created_count = 0
        for i in range(count):
            notification_type, title, message = notification_types[i % len(notification_types)]
            
            # البحث عن حجز للربط (اختياري)
            booking = Booking.objects.filter(
                customer=user
            ).first() if notification_type in ['new_message', 'booking_confirmed'] else None

            Notification.objects.create(
                recipient=user,
                notification_type=notification_type,
                title=f"{title} #{i+1}",
                message=f"{message} - إشعار تجريبي رقم {i+1}",
                booking=booking,
                is_read=False if i < count // 2 else True  # نصف الإشعارات غير مقروءة
            )
            created_count += 1

        self.stdout.write(
            self.style.SUCCESS(
                f'تم إنشاء {created_count} إشعار تجريبي للمستخدم {user.username}'
            )
        )