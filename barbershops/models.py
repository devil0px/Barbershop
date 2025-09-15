from django.db import models
from django.contrib.auth import get_user_model
from django.core.validators import MinValueValidator, MaxValueValidator
from decimal import Decimal
import json

User = get_user_model()

User = get_user_model()

class Barbershop(models.Model):
    # Core Fields
    owner = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='barbershops',
        verbose_name='المالك'
    )
    name = models.CharField(
        max_length=200,
        verbose_name='اسم المحل'
    )
    description = models.TextField(
        verbose_name='وصف المحل'
    )
    address = models.TextField(
        verbose_name='العنوان'
    )
    latitude = models.DecimalField(
        max_digits=9,
        decimal_places=6,
        blank=True,
        null=True,
        verbose_name='خط العرض'
    )
    longitude = models.DecimalField(
        max_digits=9,
        decimal_places=6,
        blank=True,
        null=True,
        verbose_name='خط الطول'
    )
    image = models.ImageField(
        upload_to='barbershops/',
        blank=True,
        null=True,
        verbose_name='صورة المحل'
    )
    phone_number = models.CharField(
        max_length=20,
        verbose_name='رقم الهاتف'
    )
    current_turn_number = models.IntegerField(
        default=0,
        verbose_name='رقم الدور الحالي',
        help_text='الرقم الذي يتم خدمته حالياً في المحل.'
    )
    email = models.EmailField(
        blank=True,
        verbose_name='البريد الإلكتروني'
    )
    opening_time = models.TimeField(
        verbose_name='وقت الفتح' # Legacy field
    )
    closing_time = models.TimeField(
        verbose_name='وقت الإغلاق' # Legacy field
    )
    is_active = models.BooleanField(
        default=True,
        verbose_name='نشط'
    )
    is_verified = models.BooleanField(
        default=True,
        verbose_name='مُتحقق منه'
    )
    created_at = models.DateTimeField(
        auto_now_add=True,
        verbose_name='تاريخ الإنشاء'
    )
    updated_at = models.DateTimeField(
        auto_now=True,
        verbose_name='تاريخ التحديث'
    )

    # Settings Fields
    is_premium = models.BooleanField(
        default=False,
        verbose_name='محل مميز'
    )
    premium_until = models.DateTimeField(
        null=True,
        blank=True,
        verbose_name='تاريخ انتهاء المميز'
    )
    theme_color = models.CharField(
        max_length=7,
        default='#007bff',
        verbose_name='لون الموضوع'
    )
    whatsapp_number = models.CharField(
        max_length=20,
        blank=True,
        verbose_name='رقم واتساب'
    )
    instagram_username = models.CharField(
        max_length=50,
        blank=True,
        verbose_name='اسم المستخدم على انستغرام'
    )
    minimum_booking_time = models.PositiveIntegerField(
        default=30,
        verbose_name='الحد الأدنى لوقت الحجز (دقائق)'
    )
    maximum_booking_time = models.PositiveIntegerField(
        default=120,
        verbose_name='الحد الأقصى لوقت الحجز (دقائق)'
    )
    working_days = models.JSONField(
        default=dict,
        verbose_name='أيام العمل'
    )
    allow_customer_photos = models.BooleanField(
        default=True,
        verbose_name='السماح بتحميل صور العملاء'
    )
    max_customer_photos = models.PositiveIntegerField(
        default=5,
        verbose_name='الحد الأقصى لصور العملاء'
    )
    require_photo_for_review = models.BooleanField(
        default=False,
        verbose_name='السماح بالصور في التقييمات'
    )
    minimum_rating_for_review = models.PositiveIntegerField(
        default=1,
        verbose_name='التقييم الأدنى المسموح به'
    )
    notify_by_email = models.BooleanField(
        default=True,
        verbose_name='إشعارات بالبريد الإلكتروني'
    )
    notify_by_sms = models.BooleanField(
        default=True,
        verbose_name='إشعارات بالرسائل القصيرة'
    )
    notify_by_whatsapp = models.BooleanField(
        default=True,
        verbose_name='إشعارات على واتساب'
    )
    allow_online_booking = models.BooleanField(
        default=True,
        verbose_name='السماح بالحجز عبر الإنترنت'
    )
    booking_advance_days = models.PositiveIntegerField(
        default=7,
        verbose_name='عدد الأيام المسموح بها للحجز المسبق'
    )
    booking_slots = models.JSONField(
        default=dict,
        verbose_name='أوقات الحجز المتاحة'
    )
    settings = models.JSONField(
        default=dict,
        verbose_name='الإعدادات المتقدمة'
    )

    class Meta:
        verbose_name = 'محل حلاقة'
        verbose_name_plural = 'محلات الحلاقة'
        unique_together = ('owner', 'name')

    def __str__(self):
        return self.name

    def save(self, *args, **kwargs):
        if not self.pk:
            self.settings = {
                'working_hours': {
                    'monday': {'start': '09:00', 'end': '18:00'},
                    'tuesday': {'start': '09:00', 'end': '18:00'},
                    'wednesday': {'start': '09:00', 'end': '18:00'},
                    'thursday': {'start': '09:00', 'end': '18:00'},
                    'friday': {'start': '10:00', 'end': '15:00'},
                    'saturday': {'start': '09:00', 'end': '18:00'},
                    'sunday': {'start': '09:00', 'end': '18:00'}
                },
                'booking_slots': {
                    'morning': {'start': '09:00', 'end': '12:00'},
                    'afternoon': {'start': '13:00', 'end': '18:00'}
                },
                'notification_settings': {
                    'new_booking': True,
                    'booking_cancelled': True,
                    'booking_reminder': True,
                    'review_received': True
                },
                'social_links': {
                    'facebook': '',
                    'instagram': '',
                    'snapchat': '',
                    'twitter': ''
                },
                'payment_methods': {
                    'cash': True,
                    'credit_card': False,
                    'debit_card': False,
                    'online_payment': False
                }
            }
        super().save(*args, **kwargs)

    def get_working_hours(self):
        return self.settings.get('working_hours', {})

    def get_booking_slots(self):
        return self.settings.get('booking_slots', {})

    def get_notification_settings(self):
        return self.settings.get('notification_settings', {})

    def get_social_links(self):
        return self.settings.get('social_links', {})

    def get_payment_methods(self):
        return self.settings.get('payment_methods', {})

    def update_settings(self, settings_data):
        self.settings.update(settings_data)
        self.save(update_fields=['settings'])

    def is_working_day(self, day):
        working_hours = self.get_working_hours()
        return day in working_hours and working_hours[day]['start'] != working_hours[day]['end']

    @property
    def average_rating(self):
        reviews = self.reviews.all()
        if reviews:
            return sum([review.rating for review in reviews]) / len(reviews)
        return 0

    @property
    def total_reviews(self):
        return self.reviews.count()

    def get_main_photo_url(self):
        main_image = self.images.filter(is_main=True).first()
        if main_image and hasattr(main_image.image, 'url'):
            return main_image.image.url
        
        first_image = self.images.first()
        if first_image and hasattr(first_image.image, 'url'):
            return first_image.image.url
            
        return None


class BarbershopImage(models.Model):
    barbershop = models.ForeignKey(
        Barbershop,
        on_delete=models.CASCADE,
        related_name='images',
        verbose_name='محل الحلاقة'
    )
    image = models.ImageField(
        upload_to='barbershops/',
        verbose_name='الصورة'
    )
    is_main = models.BooleanField(
        default=False,
        verbose_name='صورة رئيسية'
    )
    created_at = models.DateTimeField(
        auto_now_add=True,
        verbose_name='تاريخ الإضافة'
    )

    class Meta:
        verbose_name = 'صورة محل الحلاقة'
        verbose_name_plural = 'صور محلات الحلاقة'

    def __str__(self):
        return f"صورة {self.barbershop.name}"

class Service(models.Model):
    barbershop = models.ForeignKey(
        Barbershop,
        on_delete=models.CASCADE,
        related_name='services',
        verbose_name='محل الحلاقة'
    )
    
    # إضافة حقول جديدة للخدمات
    category = models.CharField(
        max_length=50,
        choices=[
            ('haircut', 'قص الشعر'),
            ('beard', 'اللحية'),
            ('shave', 'الحلاقة'),
            ('hair_color', 'صبغ الشعر'),
            ('other', 'خدمات أخرى')
        ],
        default='haircut',
        verbose_name='الفئة'
    )
    
    # تفاصيل الخدمة
    is_popular = models.BooleanField(
        default=False,
        verbose_name='خدمة شائعة'
    )
    popularity_score = models.DecimalField(
        max_digits=5,
        decimal_places=2,
        default=0,
        verbose_name='درجة الشهرة'
    )
    
    # متطلبات الخدمة
    required_tools = models.TextField(
        blank=True,
        verbose_name='الأدوات المطلوبة'
    )
    preparation_time = models.PositiveIntegerField(
        default=0,
        verbose_name='وقت التحضير (دقائق)'
    )
    
    # إعدادات الحجز
    min_booking_time = models.PositiveIntegerField(
        default=0,
        verbose_name='الحد الأدنى لوقت الحجز (دقائق)'
    )
    max_booking_time = models.PositiveIntegerField(
        default=120,
        verbose_name='الحد الأقصى لوقت الحجز (دقائق)'
    )
    
    # إحصائيات الخدمة
    total_bookings = models.PositiveIntegerField(
        default=0,
        verbose_name='إجمالي الحجوزات'
    )
    average_rating = models.DecimalField(
        max_digits=3,
        decimal_places=2,
        default=0,
        verbose_name='متوسط التقييم'
    )
    
    # إعدادات العرض
    display_order = models.PositiveIntegerField(
        default=0,
        verbose_name='ترتيب العرض'
    )
    
    # إعدادات التوافر
    available_days = models.JSONField(
        default=dict,
        verbose_name='أيام توفر الخدمة'
    )
    available_hours = models.JSONField(
        default=dict,
        verbose_name='ساعات توفر الخدمة'
    )
    name = models.CharField(
        max_length=100,
        verbose_name='اسم الخدمة'
    )
    description = models.TextField(
        blank=True,
        verbose_name='وصف الخدمة'
    )
    price = models.DecimalField(
        max_digits=8,
        decimal_places=2,
        validators=[MinValueValidator(Decimal('0.01'))],
        verbose_name='السعر'
    )
    duration = models.PositiveIntegerField(
        help_text='المدة بالدقائق',
        verbose_name='مدة الخدمة'
    )
    image = models.ImageField(
        upload_to='services/',
        blank=True,
        null=True,
        verbose_name='صورة الخدمة'
    )
    is_active = models.BooleanField(
        default=True,
        verbose_name='نشط'
    )
    created_at = models.DateTimeField(
        auto_now_add=True,
        verbose_name='تاريخ الإنشاء'
    )

    class Meta:
        verbose_name = 'خدمة'
        verbose_name_plural = 'الخدمات'

    def __str__(self):
        return f"{self.name} - {self.barbershop.name}"

class ServiceImage(models.Model):
    service = models.ForeignKey(
        Service,
        on_delete=models.CASCADE,
        related_name='images',
        verbose_name='الخدمة'
    )
    image = models.ImageField(
        upload_to='services/',
        verbose_name='الصورة'
    )
    created_at = models.DateTimeField(
        auto_now_add=True,
        verbose_name='تاريخ الإضافة'
    )

    class Meta:
        verbose_name = 'صورة الخدمة'
        verbose_name_plural = 'صور الخدمات'

    def __str__(self):
        return f"صورة {self.service.name}"
