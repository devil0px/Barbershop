from django.db import models
from django.contrib.auth import get_user_model
from barbershops.models import Barbershop, Service
from django.utils import timezone
from decimal import Decimal

User = get_user_model()

class Booking(models.Model):
    STATUS_CHOICES = (
        ('pending', 'في الانتظار'),
        ('confirmed', 'مؤكد'),
        ('completed', 'مكتمل'),
        ('cancelled', 'ملغي'),
        ('no_show', 'لم يحضر'),
    )

    customer = models.ForeignKey(
        User,
        on_delete=models.SET_NULL,
        related_name='bookings',
        verbose_name='العميل',
        null=True,
        blank=True
    )
    customer_name = models.CharField(max_length=100, verbose_name='اسم العميل', blank=True)
    customer_phone = models.CharField(max_length=20, verbose_name='رقم هاتف العميل', blank=True)
    customer_email = models.EmailField(verbose_name='البريد الإلكتروني للعميل', blank=True)
    barbershop = models.ForeignKey(
        Barbershop,
        on_delete=models.CASCADE,
        related_name='bookings',
        verbose_name='محل الحلاقة'
    )
    # سيتم استبدال هذا الحقل بعلاقة many-to-many عبر BookingService
    # نبقيه مؤقتاً للتوافق مع النظام الحالي
    service = models.ForeignKey(
        Service,
        on_delete=models.CASCADE,
        related_name='bookings',
        verbose_name='الخدمة',
        null=True,
        blank=True
    )
    
    # علاقة many-to-many مع الخدمات عبر نموذج وسيط
    services = models.ManyToManyField(
        Service,
        through='BookingService',
        related_name='multi_bookings',
        verbose_name='الخدمات المحجوزة'
    )
    booking_day = models.DateField(
        verbose_name='اليوم المحجوز له',
        null=True,
        blank=True
    )
    queue_number = models.PositiveIntegerField(
        verbose_name='رقم الدور في اليوم',
        default=1
    )
    status = models.CharField(
        max_length=20,
        choices=STATUS_CHOICES,
        default='pending',
        verbose_name='حالة الحجز'
    )
    notes = models.TextField(
        blank=True,
        null=True,
        verbose_name='ملاحظات'
    )
    total_price = models.DecimalField(
        max_digits=8,
        decimal_places=2,
        verbose_name='السعر الإجمالي'
    )
    created_at = models.DateTimeField(
        auto_now_add=True,
        verbose_name='تاريخ الإنشاء'
    )
    updated_at = models.DateTimeField(
        auto_now=True,
        verbose_name='تاريخ التحديث'
    )

    class Meta:
        verbose_name = 'حجز'
        verbose_name_plural = 'الحجوزات'
        ordering = ['-booking_day', 'queue_number']

    def __str__(self):
        if self.customer:
            return f"{self.customer.username} - {self.barbershop.name} - {self.booking_day} - دور {self.queue_number}"
        return f"{self.customer_name} - {self.barbershop.name} - {self.booking_day} - دور {self.queue_number}"

    @property
    def is_today(self):
        """Checks if the booking is for the current day."""
        if self.booking_day is None:
            return False
        return self.booking_day == timezone.now().date()

    @property
    def is_past_due(self):
        # In queue system, booking is 'past due' if booking_day is before today
        if self.booking_day is None:
            return False
        return self.booking_day < timezone.now().date()

    def can_be_cancelled(self):
        """يمكن إلغاء الحجز إذا كان اليوم المحجوز له لم يأتِ بعد"""
        if self.booking_day is None:
            return False
        return self.booking_day > timezone.now().date()

    def unread_messages(self):
        """هل هناك رسائل غير مقروءة من الطرف الآخر"""
        # تصفية الرسائل غير المقروءة من الطرف الآخر
        if self.customer:
            return self.messages.filter(
                is_read=False
            ).exclude(
                sender=self.customer
            ).exists()
        return False

    def get_status_class(self):
        """إرجاع CSS class حسب حالة الحجز"""
        status_classes = {
            'pending': 'bg-warning text-dark',
            'confirmed': 'bg-success text-white',
            'completed': 'bg-info text-white',
            'cancelled': 'bg-danger text-white',
            'no_show': 'bg-secondary text-white',
        }
        return status_classes.get(self.status, 'bg-secondary text-white')

    def get_status_display_arabic(self):
        """إرجاع اسم الحالة بالعربية"""
        status_display = {
            'pending': 'في الانتظار',
            'confirmed': 'مؤكد',
            'completed': 'مكتمل',
            'cancelled': 'ملغي',
            'no_show': 'لم يحضر',
        }
        return status_display.get(self.status, self.status)
    
    def get_total_services_price(self):
        """حساب إجمالي أسعار الخدمات المحجوزة"""
        total = Decimal('0.00')
        for booking_service in self.booking_services.all():
            total += booking_service.service.price * booking_service.quantity
        return total
    
    def get_total_duration(self):
        """حساب إجمالي مدة الخدمات المحجوزة"""
        total_minutes = 0
        for booking_service in self.booking_services.all():
            total_minutes += booking_service.service.duration * booking_service.quantity
        return total_minutes
    
    def get_services_list(self):
        """إرجاع قائمة بأسماء الخدمات المحجوزة"""
        services = []
        for booking_service in self.booking_services.all():
            if booking_service.quantity > 1:
                services.append(f"{booking_service.service.name} (x{booking_service.quantity})")
            else:
                services.append(booking_service.service.name)
        return services

class BookingService(models.Model):
    """نموذج وسيط لربط الحجوزات بالخدمات المتعددة"""
    booking = models.ForeignKey(
        Booking,
        on_delete=models.CASCADE,
        related_name='booking_services',
        verbose_name='الحجز'
    )
    service = models.ForeignKey(
        Service,
        on_delete=models.CASCADE,
        related_name='service_bookings',
        verbose_name='الخدمة'
    )
    quantity = models.PositiveIntegerField(
        default=1,
        verbose_name='الكمية'
    )
    price_at_booking = models.DecimalField(
        max_digits=8,
        decimal_places=2,
        verbose_name='السعر وقت الحجز',
        help_text='سعر الخدمة وقت إنشاء الحجز'
    )
    notes = models.TextField(
        blank=True,
        verbose_name='ملاحظات خاصة بالخدمة'
    )
    created_at = models.DateTimeField(
        auto_now_add=True,
        verbose_name='تاريخ الإضافة'
    )
    
    class Meta:
        verbose_name = 'خدمة الحجز'
        verbose_name_plural = 'خدمات الحجوزات'
        unique_together = ['booking', 'service']
        ordering = ['created_at']
    
    def __str__(self):
        if self.quantity > 1:
            return f"{self.service.name} (x{self.quantity}) - {self.booking}"
        return f"{self.service.name} - {self.booking}"
    
    def get_total_price(self):
        """حساب السعر الإجمالي للخدمة (السعر × الكمية)"""
        return self.price_at_booking * self.quantity
    
    def get_total_duration(self):
        """حساب المدة الإجمالية للخدمة (المدة × الكمية)"""
        return self.service.duration * self.quantity
    
    def save(self, *args, **kwargs):
        # حفظ سعر الخدمة وقت الحجز إذا لم يكن محدداً
        if not self.price_at_booking:
            self.price_at_booking = self.service.price
        super().save(*args, **kwargs)


class BookingHistory(models.Model):
    booking = models.ForeignKey(
        Booking,
        on_delete=models.CASCADE,
        related_name='history',
        verbose_name='الحجز'
    )
    old_status = models.CharField(
        max_length=20,
        choices=Booking.STATUS_CHOICES,
        default='pending',
        verbose_name='الحالة السابقة'
    )
    new_status = models.CharField(
        max_length=20,
        choices=Booking.STATUS_CHOICES,
        default='pending',
        verbose_name='الحالة الجديدة'
    )
    changed_by = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        verbose_name='تم التغيير بواسطة'
    )
    notes = models.TextField(
        blank=True,
        verbose_name='ملاحظات'
    )
    created_at = models.DateTimeField(
        auto_now_add=True,
        verbose_name='تاريخ التغيير'
    )

    class Meta:
        verbose_name = 'تاريخ الحجز'
        verbose_name_plural = 'تاريخ الحجوزات'
        ordering = ['-created_at']

    def __str__(self):
        return f"{self.booking} - {self.get_status_display()}"


class BookingMessage(models.Model):
    booking = models.ForeignKey(
        Booking,
        on_delete=models.CASCADE,
        related_name='messages',
        verbose_name='الحجز'
    )
    sender = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        verbose_name='المرسل'
    )
    message = models.TextField(verbose_name='الرسالة')
    is_read = models.BooleanField(default=False, verbose_name='تم قرائتها')
    created_at = models.DateTimeField(auto_now_add=True, verbose_name='وقت الإرسال')
    
    class Meta:
        verbose_name = 'رسالة حجز'
        verbose_name_plural = 'رسائل الحجوزات'
        ordering = ['created_at']
    
    def __str__(self):
        return f'{self.sender.username}: {self.message[:50]}'

    @property
    def is_unread(self):
        """هل الرسالة غير مقروءة"""
        return not self.is_read



