"""
أمر Django لتطبيق تحسينات الأداء
Performance Optimization Management Command

استخدام: python manage.py optimize_performance
"""

from django.core.management.base import BaseCommand
from django.core.cache import cache
from django.db import connection
from django.utils import timezone
import logging

logger = logging.getLogger(__name__)

class Command(BaseCommand):
    help = 'تطبيق تحسينات الأداء على المشروع'

    def add_arguments(self, parser):
        parser.add_argument(
            '--clear-cache',
            action='store_true',
            help='مسح الكاش قبل التحسين',
        )
        parser.add_argument(
            '--warm-cache',
            action='store_true',
            help='تسخين الكاش بعد التحسين',
        )
        parser.add_argument(
            '--apply-indexes',
            action='store_true',
            help='تطبيق فهارس قاعدة البيانات',
        )

    def handle(self, *args, **options):
        self.stdout.write(
            self.style.SUCCESS('🚀 بدء تطبيق تحسينات الأداء...')
        )

        # مسح الكاش إذا طُلب ذلك
        if options['clear_cache']:
            self.clear_cache()

        # تطبيق فهارس قاعدة البيانات
        if options['apply_indexes']:
            self.apply_database_indexes()

        # تسخين الكاش
        if options['warm_cache']:
            self.warm_up_cache()

        # تطبيق التحسينات العامة
        self.apply_general_optimizations()

        self.stdout.write(
            self.style.SUCCESS('✅ تم تطبيق تحسينات الأداء بنجاح!')
        )

    def clear_cache(self):
        """مسح الكاش"""
        self.stdout.write('🧹 مسح الكاش...')
        cache.clear()
        self.stdout.write(
            self.style.SUCCESS('✅ تم مسح الكاش بنجاح')
        )

    def apply_database_indexes(self):
        """تطبيق فهارس قاعدة البيانات"""
        self.stdout.write('📊 تطبيق فهارس قاعدة البيانات...')
        
        indexes = [
            # فهارس الحجوزات
            "CREATE INDEX IF NOT EXISTS idx_booking_barbershop_day ON bookings_booking(barbershop_id, booking_day);",
            "CREATE INDEX IF NOT EXISTS idx_booking_customer_status ON bookings_booking(customer_id, status);",
            "CREATE INDEX IF NOT EXISTS idx_booking_created_at ON bookings_booking(created_at DESC);",
            
            # فهارس الصالونات
            "CREATE INDEX IF NOT EXISTS idx_barbershop_active_verified ON barbershops_barbershop(is_active, is_verified);",
            "CREATE INDEX IF NOT EXISTS idx_barbershop_owner ON barbershops_barbershop(owner_id);",
            
            # فهارس الخدمات
            "CREATE INDEX IF NOT EXISTS idx_service_barbershop_active ON barbershops_service(barbershop_id, is_active);",
            "CREATE INDEX IF NOT EXISTS idx_service_category ON barbershops_service(category);",
            
            # فهارس التقييمات
            "CREATE INDEX IF NOT EXISTS idx_review_barbershop_approved ON reviews_review(barbershop_id, is_approved);",
            "CREATE INDEX IF NOT EXISTS idx_review_customer ON reviews_review(customer_id);",
            
            # فهارس الإشعارات
            "CREATE INDEX IF NOT EXISTS idx_notification_user_read ON notifications_notification(user_id, is_read);",
            "CREATE INDEX IF NOT EXISTS idx_notification_created_at ON notifications_notification(created_at DESC);",
        ]

        with connection.cursor() as cursor:
            for index_sql in indexes:
                try:
                    cursor.execute(index_sql)
                    self.stdout.write(f'  ✅ {index_sql[:50]}...')
                except Exception as e:
                    self.stdout.write(
                        self.style.ERROR(f'  ❌ خطأ في تطبيق الفهرس: {e}')
                    )

        self.stdout.write(
            self.style.SUCCESS('✅ تم تطبيق فهارس قاعدة البيانات')
        )

    def warm_up_cache(self):
        """تسخين الكاش"""
        self.stdout.write('🔥 تسخين الكاش...')
        
        try:
            from barbershops.models import Barbershop
            from bookings.models import Booking
            from reviews.models import Review
            from django.db.models import Count, Avg
            
            # تسخين كاش الصالونات الشائعة
            popular_barbershops = Barbershop.objects.filter(
                is_active=True,
                is_verified=True
            ).annotate(
                bookings_count=Count('bookings')
            ).order_by('-bookings_count')[:10]
            
            for barbershop in popular_barbershops:
                # حفظ إحصائيات الصالون في الكاش
                stats = {
                    'total_bookings': barbershop.bookings.count(),
                    'avg_rating': barbershop.reviews.filter(
                        is_approved=True
                    ).aggregate(avg=Avg('rating'))['avg'] or 0,
                    'total_reviews': barbershop.reviews.filter(is_approved=True).count(),
                    'services_count': barbershop.services.filter(is_active=True).count(),
                }
                
                cache.set(f'barbershop_stats_{barbershop.id}', stats, 3600)
                self.stdout.write(f'  ✅ تم تسخين كاش الصالون: {barbershop.name}')
            
            # تسخين كاش حجوزات اليوم
            today = timezone.now().date()
            today_bookings = Booking.objects.filter(
                booking_day=today
            ).select_related('barbershop', 'customer', 'service')
            
            cache.set('today_bookings_count', today_bookings.count(), 300)
            
            self.stdout.write(
                self.style.SUCCESS('✅ تم تسخين الكاش بنجاح')
            )
            
        except Exception as e:
            self.stdout.write(
                self.style.ERROR(f'❌ خطأ في تسخين الكاش: {e}')
            )

    def apply_general_optimizations(self):
        """تطبيق التحسينات العامة"""
        self.stdout.write('⚙️ تطبيق التحسينات العامة...')
        
        try:
            # تنظيف الجلسات المنتهية الصلاحية
            from django.core.management import call_command
            call_command('clearsessions')
            self.stdout.write('  ✅ تم تنظيف الجلسات المنتهية الصلاحية')
            
            # جمع الملفات الثابتة (في الإنتاج)
            from django.conf import settings
            if not settings.DEBUG:
                call_command('collectstatic', '--noinput')
                self.stdout.write('  ✅ تم جمع الملفات الثابتة')
            
            self.stdout.write(
                self.style.SUCCESS('✅ تم تطبيق التحسينات العامة')
            )
            
        except Exception as e:
            self.stdout.write(
                self.style.ERROR(f'❌ خطأ في التحسينات العامة: {e}')
            )
