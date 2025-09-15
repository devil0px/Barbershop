from django.contrib.auth.models import AbstractUser
from django.db import models
from django.core.validators import RegexValidator
from django.utils import timezone
from django.core.mail import send_mail
from django.conf import settings
from django.urls import reverse
import uuid
import secrets
import string

class CustomUser(AbstractUser):
    username = models.CharField(max_length=150, unique=True, error_messages={'unique': 'A user with that username already exists.'})
    email = models.EmailField(unique=True, verbose_name='البريد الإلكتروني')
    USER_TYPE_CHOICES = (
        ('customer', 'عميل'),
        ('barber', 'صاحب محل حلاقة'),
    )
    user_type = models.CharField(
        max_length=10,
        choices=USER_TYPE_CHOICES,
        default='customer',
        verbose_name='نوع المستخدم',
        unique=False,
        null=True  # Allow null values in the database
    )
    phone_number = models.CharField(
        max_length=15,
        validators=[RegexValidator(regex=r'^\+?1?\d{9,15}$', message="أدخل رقم هاتف صالح.")],
        verbose_name='رقم الهاتف',
        unique=True,
        null=True,  # Allow null values in the database
        blank=True, # Allow the field to be blank in forms
        help_text='يجب أن يكون فريدًا.'
    )
    profile_photo = models.ImageField(
        upload_to='profiles/',
        blank=True,
        null=True,
        verbose_name='صورة الملف الشخصي'
    )
    
    # حقول نظام التفعيل
    is_email_verified = models.BooleanField(
        default=False,
        verbose_name='تم تفعيل الإيميل'
    )
    activation_code = models.CharField(
        max_length=6,
        blank=True,
        null=True,
        verbose_name='كود التفعيل'
    )
    activation_code_created = models.DateTimeField(
        blank=True,
        null=True,
        verbose_name='تاريخ إنشاء كود التفعيل'
    )
    activation_token = models.UUIDField(
        default=uuid.uuid4,
        editable=False,
        verbose_name='رمز التفعيل'
    )

    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = ['username']

    def __str__(self):
        return self.email

    def get_full_name(self):
        """إرجاع الاسم الكامل للمستخدم"""
        if self.first_name and self.last_name:
            return f"{self.first_name} {self.last_name}"
        return self.username

    def get_profile_photo_url(self):
        """إرجاع رابط صورة الملف الشخصي أو صورة افتراضية"""
        if self.profile_photo and hasattr(self.profile_photo, 'url'):
            return self.profile_photo.url
        return None
    
    def generate_activation_code(self):
        """إنشاء كود تفعيل جديد"""
        self.activation_code = ''.join(secrets.choice(string.digits) for _ in range(6))
        self.activation_code_created = timezone.now()
        self.activation_token = uuid.uuid4()
        self.save()
        return self.activation_code
    
    def is_activation_code_valid(self):
        """التحقق من صحة كود التفعيل (صالح لمدة 24 ساعة)"""
        if not self.activation_code_created:
            return False
        
        expiry_time = self.activation_code_created + timezone.timedelta(hours=24)
        return timezone.now() < expiry_time
    
    def activate_account(self, code):
        """تفعيل الحساب باستخدام الكود"""
        import logging
        logger = logging.getLogger(__name__)
        
        # تسجيل مفصل للتشخيص
        logger.info(f"Activation attempt for user {self.email}:")
        logger.info(f"  - Input code: '{code}' (type: {type(code)}, length: {len(str(code))})")
        logger.info(f"  - Stored code: '{self.activation_code}' (type: {type(self.activation_code)}, length: {len(str(self.activation_code)) if self.activation_code else 0})")
        logger.info(f"  - Code match: {self.activation_code == code}")
        logger.info(f"  - Code valid: {self.is_activation_code_valid()}")
        
        # تنظيف الكود من المسافات والأحرف غير المرغوب فيها
        code_cleaned = str(code).strip()
        stored_code_cleaned = str(self.activation_code).strip() if self.activation_code else ""
        
        logger.info(f"  - Cleaned input code: '{code_cleaned}'")
        logger.info(f"  - Cleaned stored code: '{stored_code_cleaned}'")
        logger.info(f"  - Cleaned codes match: {stored_code_cleaned == code_cleaned}")
        
        # التحقق من صحة الكود
        if stored_code_cleaned == code_cleaned and self.is_activation_code_valid():
            logger.info("Activation successful!")
            self.is_email_verified = True
            self.is_active = True
            self.activation_code = None
            self.activation_code_created = None
            self.save()
            return True
        
        logger.warning("Activation failed!")
        return False
    
    def send_activation_email(self, request=None):
        """إرسال إيميل التفعيل"""
        if not self.activation_code:
            self.generate_activation_code()
        
        subject = f'تفعيل حساب {settings.SITE_NAME if hasattr(settings, "SITE_NAME") else "Barber Shop"}'
        
        # إنشاء رابط التفعيل
        if request:
            domain = request.get_host()
            protocol = 'https' if request.is_secure() else 'http'
        else:
            domain = getattr(settings, 'SITE_DOMAIN', 'localhost:8000')
            protocol = 'http'
        
        activation_url = f"{protocol}://{domain}{reverse('accounts:activate', kwargs={'token': self.activation_token})}"
        
        message = f"""
مرحباً {self.get_full_name()},

شكراً لك على التسجيل في موقعنا!

لتفعيل حسابك، يرجى استخدام أحد الطرق التالية:

الطريقة الأولى - كود التفعيل:
كود التفعيل الخاص بك هو: {self.activation_code}

الطريقة الثانية - رابط التفعيل:
اضغط على الرابط التالي لتفعيل حسابك:
{activation_url}

ملاحظة: هذا الكود صالح لمدة 24 ساعة فقط.

إذا لم تقم بإنشاء هذا الحساب، يرجى تجاهل هذا الإيميل.

مع تحيات فريق العمل
        """
        
        try:
            send_mail(
                subject,
                message,
                settings.DEFAULT_FROM_EMAIL,
                [self.email],
                fail_silently=False,
            )
            return True
        except Exception as e:
            print(f"خطأ في إرسال الإيميل: {e}")
            return False
    
    def save(self, *args, **kwargs):
        # إذا كان حساب جديد وغير مفعل، قم بتعطيله حتى يتم التفعيل
        if not self.pk and not self.is_email_verified:
            self.is_active = False
        super().save(*args, **kwargs)