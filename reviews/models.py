from django.db import models
from django.contrib.auth import get_user_model
from django.core.validators import MinValueValidator, MaxValueValidator
from barbershops.models import Barbershop
from bookings.models import Booking

User = get_user_model()

class Review(models.Model):
    customer = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='reviews',
        verbose_name='العميل'
    )
    barbershop = models.ForeignKey(
        Barbershop,
        on_delete=models.CASCADE,
        related_name='reviews',
        verbose_name='محل الحلاقة'
    )
    booking = models.OneToOneField(
        Booking,
        on_delete=models.CASCADE,
        related_name='review',
        verbose_name='الحجز',
        blank=True,
        null=True
    )
    rating = models.IntegerField(
        validators=[MinValueValidator(1), MaxValueValidator(5)],
        verbose_name='التقييم'
    )
    comment = models.TextField(
        verbose_name='التعليق'
    )
    is_approved = models.BooleanField(
        default=True,
        verbose_name='موافق عليه'
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
        verbose_name = 'تقييم'
        verbose_name_plural = 'التقييمات'
        ordering = ['-created_at']
        unique_together = ['customer', 'barbershop', 'booking']

    def __str__(self):
        return f"{self.customer.username} - {self.barbershop.name} - {self.rating} نجوم"

class ReviewImage(models.Model):
    review = models.ForeignKey(
        Review,
        on_delete=models.CASCADE,
        related_name='images',
        verbose_name='التقييم'
    )
    image = models.ImageField(
        upload_to='reviews/',
        verbose_name='الصورة'
    )
    created_at = models.DateTimeField(
        auto_now_add=True,
        verbose_name='تاريخ الإضافة'
    )

    class Meta:
        verbose_name = 'صورة التقييم'
        verbose_name_plural = 'صور التقييمات'

    def __str__(self):
        return f"صورة تقييم {self.review.barbershop.name}"
