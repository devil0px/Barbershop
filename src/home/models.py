from django.db import models
from django.core.validators import FileExtensionValidator


class SiteSettings(models.Model):
    """إعدادات الموقع العامة"""
    
    # معلومات الموقع الأساسية
    site_name = models.CharField(max_length=100, default="Barber Shop", verbose_name="اسم الموقع")
    site_description = models.TextField(default="أفضل صالون حلاقة في المدينة", verbose_name="وصف الموقع")
    hero_title = models.CharField(max_length=200, default="أفضل صالون حلاقة في المدينة", verbose_name="عنوان البانر الرئيسي")
    hero_subtitle = models.TextField(
        default="منذ عام 1973، نقدم خدمات حلاقة عالية الجودة مع التركيز على الحرفية والاهتمام بالتفاصيل.",
        verbose_name="وصف البانر الرئيسي"
    )
    
    # قسم "عنا"
    about_title = models.CharField(max_length=200, default="خبرة تمتد لأكثر من 50 عاماً", verbose_name="عنوان قسم عنا")
    about_description = models.TextField(
        default="منذ عام 1973، نحن نقدم أفضل خدمات الحلاقة في المدينة. فريقنا من الحلاقين المحترفين يجمع بين التقنيات التقليدية والأساليب الحديثة لنمنحك مظهراً مميزاً.",
        verbose_name="وصف قسم عنا"
    )
    
    # الصور
    about_image_1 = models.ImageField(
        upload_to='about_images/',
        null=True,
        blank=True,
        validators=[FileExtensionValidator(allowed_extensions=['jpg', 'jpeg', 'png', 'webp'])],
        verbose_name="الصورة الأولى"
    )
    about_image_1_alt = models.CharField(max_length=100, default="صورة المحل", verbose_name="وصف الصورة الأولى")
    
    about_image_2 = models.ImageField(
        upload_to='about_images/',
        null=True,
        blank=True,
        validators=[FileExtensionValidator(allowed_extensions=['jpg', 'jpeg', 'png', 'webp'])],
        verbose_name="الصورة الثانية"
    )
    about_image_2_alt = models.CharField(max_length=100, default="فريق العمل", verbose_name="وصف الصورة الثانية")
    
    about_image_3 = models.ImageField(
        upload_to='about_images/',
        null=True,
        blank=True,
        validators=[FileExtensionValidator(allowed_extensions=['jpg', 'jpeg', 'png', 'webp'])],
        verbose_name="الصورة الثالثة"
    )
    about_image_3_alt = models.CharField(max_length=100, default="أدوات الحلاقة", verbose_name="وصف الصورة الثالثة")
    
    # معلومات الاتصال
    phone_number = models.CharField(max_length=20, default="+20109841514", verbose_name="رقم الهاتف")
    email = models.EmailField(default="info@barbershop.com", verbose_name="البريد الإلكتروني")
    address = models.CharField(max_length=200, default="مدينتي - اسم الشارع", verbose_name="العنوان")
    working_hours = models.CharField(max_length=100, default="يومياً من 8:00 ص إلى 10:00 م", verbose_name="ساعات العمل")
    
    # روابط التواصل الاجتماعي
    facebook_url = models.URLField(blank=True, null=True, verbose_name="رابط فيسبوك")
    instagram_url = models.URLField(blank=True, null=True, verbose_name="رابط إنستغرام")
    twitter_url = models.URLField(blank=True, null=True, verbose_name="رابط تويتر")
    whatsapp_number = models.CharField(max_length=20, blank=True, null=True, verbose_name="رقم واتساب")
    
    # تواريخ التحديث
    created_at = models.DateTimeField(auto_now_add=True, verbose_name="تاريخ الإنشاء")
    updated_at = models.DateTimeField(auto_now=True, verbose_name="تاريخ التحديث")
    
    class Meta:
        verbose_name = "إعدادات الموقع"
        verbose_name_plural = "إعدادات الموقع"
    
    def __str__(self):
        return f"إعدادات {self.site_name}"
    
    def save(self, *args, **kwargs):
        # التأكد من وجود سجل واحد فقط
        if not self.pk and SiteSettings.objects.exists():
            raise ValueError("يمكن إنشاء سجل واحد فقط من إعدادات الموقع")
        super().save(*args, **kwargs)
    
    @classmethod
    def get_settings(cls):
        """الحصول على إعدادات الموقع أو إنشاء إعدادات افتراضية"""
        settings, created = cls.objects.get_or_create(pk=1)
        return settings


class HomePageFeature(models.Model):
    """ميزات الصفحة الرئيسية (قسم عنا - النقاط المميزة)"""
    
    title = models.CharField(max_length=100, verbose_name="العنوان")
    description = models.TextField(blank=True, verbose_name="الوصف")
    icon = models.CharField(
        max_length=50,
        default="fas fa-check-circle",
        verbose_name="أيقونة (Font Awesome class)",
        help_text="مثال: fas fa-check-circle"
    )
    order = models.PositiveIntegerField(default=0, verbose_name="الترتيب")
    is_active = models.BooleanField(default=True, verbose_name="نشط")
    
    created_at = models.DateTimeField(auto_now_add=True, verbose_name="تاريخ الإنشاء")
    updated_at = models.DateTimeField(auto_now=True, verbose_name="تاريخ التحديث")
    
    class Meta:
        verbose_name = "ميزة الصفحة الرئيسية"
        verbose_name_plural = "ميزات الصفحة الرئيسية"
        ordering = ['order', 'id']
    
    def __str__(self):
        return self.title


class Testimonial(models.Model):
    """شهادات العملاء"""
    
    customer_name = models.CharField(max_length=100, verbose_name="اسم العميل")
    customer_image = models.ImageField(
        upload_to='testimonials/',
        null=True,
        blank=True,
        validators=[FileExtensionValidator(allowed_extensions=['jpg', 'jpeg', 'png', 'webp'])],
        verbose_name="صورة العميل"
    )
    testimonial_text = models.TextField(verbose_name="نص الشهادة")
    rating = models.PositiveIntegerField(
        choices=[(i, i) for i in range(1, 6)],
        default=5,
        verbose_name="التقييم"
    )
    position = models.CharField(max_length=100, blank=True, verbose_name="المنصب/الوظيفة")
    is_featured = models.BooleanField(default=False, verbose_name="مميز")
    is_active = models.BooleanField(default=True, verbose_name="نشط")
    order = models.PositiveIntegerField(default=0, verbose_name="الترتيب")
    
    created_at = models.DateTimeField(auto_now_add=True, verbose_name="تاريخ الإنشاء")
    updated_at = models.DateTimeField(auto_now=True, verbose_name="تاريخ التحديث")
    
    class Meta:
        verbose_name = "شهادة عميل"
        verbose_name_plural = "شهادات الع��لاء"
        ordering = ['-is_featured', 'order', '-created_at']
    
    def __str__(self):
        return f"شهادة {self.customer_name}"


class HeroSlide(models.Model):
    """شرائح البانر الرئيسي"""
    
    title = models.CharField(max_length=200, verbose_name="العنوان")
    subtitle = models.TextField(verbose_name="العنوان الفرعي")
    background_image = models.ImageField(
        upload_to='hero_slides/',
        validators=[FileExtensionValidator(allowed_extensions=['jpg', 'jpeg', 'png', 'webp'])],
        verbose_name="صورة الخلفية"
    )
    button_text = models.CharField(max_length=50, default="احجز الآن", verbose_name="نص الزر")
    button_url = models.CharField(max_length=200, default="/barbershops/", verbose_name="رابط الزر")
    is_active = models.BooleanField(default=True, verbose_name="نشط")
    order = models.PositiveIntegerField(default=0, verbose_name="الترتيب")
    
    created_at = models.DateTimeField(auto_now_add=True, verbose_name="تاريخ الإنشاء")
    updated_at = models.DateTimeField(auto_now=True, verbose_name="تاريخ التحديث")
    
    class Meta:
        verbose_name = "شريحة البانر"
        verbose_name_plural = "شرائح البانر"
        ordering = ['order', 'id']
    
    def __str__(self):
        return self.title