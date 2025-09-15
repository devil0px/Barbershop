"""
إعدادات محسنة للأداء - مشروع إدارة الحلاقة
Optimized Performance Settings for Barbershop Management System

هذا الملف يحتوي على إعدادات Django محسنة لتحسين الأداء
"""

from .settings import *
import os

# ================================
# إعدادات الكاش المحسنة
# ================================

# استخدام Redis للكاش إذا كان متوفراً، وإلا استخدام الذاكرة المحلية
try:
    import redis
    CACHES = {
        'default': {
            'BACKEND': 'django_redis.cache.RedisCache',
            'LOCATION': 'redis://127.0.0.1:6379/1',
            'OPTIONS': {
                'CLIENT_CLASS': 'django_redis.client.DefaultClient',
                'COMPRESSOR': 'django_redis.compressors.zlib.ZlibCompressor',
                'IGNORE_EXCEPTIONS': True,
            },
            'KEY_PREFIX': 'barbershop',
            'TIMEOUT': 3600,  # ساعة واحدة
        },
        'sessions': {
            'BACKEND': 'django_redis.cache.RedisCache',
            'LOCATION': 'redis://127.0.0.1:6379/2',
            'TIMEOUT': 86400,  # يوم واحد
        }
    }
    
    # استخدام Redis للجلسات
    SESSION_ENGINE = 'django.contrib.sessions.backends.cache'
    SESSION_CACHE_ALIAS = 'default'
    
except ImportError:
    # استخدام كاش الذاكرة المحلية كبديل
    CACHES = {
        'default': {
            'BACKEND': 'django.core.cache.backends.locmem.LocMemCache',
            'LOCATION': 'barbershop-cache',
            'TIMEOUT': 3600,
            'OPTIONS': {
                'MAX_ENTRIES': 1000,
                'CULL_FREQUENCY': 3,
            }
        }
    }

# ================================
# إعدادات قاعدة البيانات المحسنة
# ================================

# تحسين إعدادات SQLite
DATABASES['default'].update({
    'OPTIONS': {
        'timeout': 20,
        'check_same_thread': False,
        # تحسينات SQLite للأداء
        'init_command': '''
            PRAGMA journal_mode=WAL;
            PRAGMA synchronous=NORMAL;
            PRAGMA cache_size=1000;
            PRAGMA temp_store=MEMORY;
            PRAGMA mmap_size=268435456;
        '''
    }
})

# ================================
# إعدادات الجلسات المحسنة
# ================================

SESSION_COOKIE_AGE = 86400  # يوم واحد
SESSION_SAVE_EVERY_REQUEST = False
SESSION_EXPIRE_AT_BROWSER_CLOSE = False
SESSION_COOKIE_HTTPONLY = True
SESSION_COOKIE_SECURE = not DEBUG  # آمن في الإنتاج فقط

# ================================
# إعدادات الملفات الثابتة المحسنة
# ================================

# استخدام WhiteNoise مع الضغط
STATICFILES_STORAGE = 'whitenoise.storage.CompressedManifestStaticFilesStorage'

# إعدادات WhiteNoise
WHITENOISE_USE_FINDERS = True
WHITENOISE_AUTOREFRESH = DEBUG
WHITENOISE_MAX_AGE = 31536000 if not DEBUG else 0  # سنة واحدة في الإنتاج

# ضغط الملفات الثابتة
WHITENOISE_SKIP_COMPRESS_EXTENSIONS = ['jpg', 'jpeg', 'png', 'gif', 'webp', 'zip', 'gz', 'tgz', 'bz2', 'tbz', 'xz', 'br']

# ================================
# إعدادات القوالب المحسنة
# ================================

# تفعيل كاش القوالب في الإنتاج
if not DEBUG:
    TEMPLATES[0]['OPTIONS']['loaders'] = [
        ('django.template.loaders.cached.Loader', [
            'django.template.loaders.filesystem.Loader',
            'django.template.loaders.app_directories.Loader',
        ]),
    ]

# ================================
# إعدادات الأمان المحسنة
# ================================

# تحسين أمان الكوكيز
CSRF_COOKIE_HTTPONLY = True
CSRF_COOKIE_SECURE = not DEBUG
CSRF_USE_SESSIONS = True

# إعدادات HTTPS في الإنتاج
if not DEBUG:
    SECURE_SSL_REDIRECT = True
    SECURE_HSTS_SECONDS = 31536000
    SECURE_HSTS_INCLUDE_SUBDOMAINS = True
    SECURE_HSTS_PRELOAD = True
    SECURE_CONTENT_TYPE_NOSNIFF = True
    SECURE_BROWSER_XSS_FILTER = True

# ================================
# إعدادات الضغط والتحسين
# ================================

# تفعيل ضغط GZip
USE_GZIP = True

# إعدادات الوسائط
MEDIA_URL = '/media/'
MEDIA_ROOT = os.path.join(BASE_DIR, 'media')

# تحسين رفع الملفات
FILE_UPLOAD_MAX_MEMORY_SIZE = 5242880  # 5MB
DATA_UPLOAD_MAX_MEMORY_SIZE = 5242880  # 5MB

# ================================
# إعدادات التسجيل المحسنة
# ================================

LOGGING.update({
    'handlers': {
        'file': {
            'level': 'INFO',
            'class': 'logging.handlers.RotatingFileHandler',
            'filename': os.path.join(BASE_DIR, 'logs', 'performance.log'),
            'maxBytes': 1024*1024*5,  # 5MB
            'backupCount': 5,
            'formatter': 'verbose',
        },
        'cache': {
            'level': 'DEBUG',
            'class': 'logging.handlers.RotatingFileHandler',
            'filename': os.path.join(BASE_DIR, 'logs', 'cache.log'),
            'maxBytes': 1024*1024*2,  # 2MB
            'backupCount': 3,
            'formatter': 'simple',
        },
    },
    'loggers': {
        'performance': {
            'handlers': ['file', 'console'],
            'level': 'INFO',
            'propagate': False,
        },
        'django.cache': {
            'handlers': ['cache'],
            'level': 'DEBUG' if DEBUG else 'INFO',
            'propagate': False,
        },
    },
})

# ================================
# إعدادات Django Channels المحسنة
# ================================

# استخدام Redis لـ Channels إذا كان متوفراً
try:
    import channels_redis
    CHANNEL_LAYERS = {
        "default": {
            "BACKEND": "channels_redis.core.RedisChannelLayer",
            "CONFIG": {
                "hosts": [("127.0.0.1", 6379)],
                "capacity": 1500,
                "expiry": 60,
            },
        },
    }
except ImportError:
    # استخدام الذاكرة المحلية كبديل
    CHANNEL_LAYERS = {
        "default": {
            "BACKEND": "channels.layers.InMemoryChannelLayer",
            "CONFIG": {
                "capacity": 300,
                "expiry": 60,
            }
        }
    }

# ================================
# إعدادات إضافية للأداء
# ================================

# تحسين استعلامات قاعدة البيانات
DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'

# تحسين معالجة الطلبات
DATA_UPLOAD_MAX_NUMBER_FIELDS = 1000

# إعدادات المنطقة الزمنية
USE_TZ = True
TIME_ZONE = 'Africa/Cairo'

# تحسين معالجة الأخطاء
if not DEBUG:
    ADMINS = [
        ('Admin', 'admin@barbershop.com'),
    ]
    MANAGERS = ADMINS
    
    # إرسال تقارير الأخطاء
    EMAIL_SUBJECT_PREFIX = '[Barbershop Error] '
    SERVER_EMAIL = 'server@barbershop.com'

# ================================
# إعدادات مخصصة للتطبيق
# ================================

# إعدادات الكاش للتطبيق
CACHE_TIMEOUT = {
    'barbershop_list': 1800,      # 30 دقيقة
    'barbershop_detail': 900,     # 15 دقيقة
    'services': 3600,             # ساعة واحدة
    'reviews': 1800,              # 30 دقيقة
    'bookings_today': 300,        # 5 دقائق
    'user_bookings': 600,         # 10 دقائق
}

# إعدادات الأداء للتطبيق
PERFORMANCE_SETTINGS = {
    'ENABLE_QUERY_OPTIMIZATION': True,
    'ENABLE_CACHE': True,
    'CACHE_WARM_UP_ON_START': not DEBUG,
    'MAX_BOOKINGS_PER_PAGE': 20,
    'MAX_REVIEWS_PER_PAGE': 10,
    'MAX_SERVICES_PER_BARBERSHOP': 50,
}

# تحسين معالجة الصور
if 'PIL' in sys.modules:
    # إعدادات معالجة الصور
    IMAGE_QUALITY = 85
    IMAGE_MAX_SIZE = (1200, 1200)
    THUMBNAIL_SIZE = (300, 300)

# ================================
# إعدادات المراقبة والتحليل
# ================================

# تفعيل مراقبة الأداء في الإنتاج
if not DEBUG:
    # يمكن إضافة أدوات مراقبة مثل Sentry
    pass

# إعدادات التحليل
ANALYTICS_ENABLED = not DEBUG
PERFORMANCE_MONITORING = not DEBUG

print("✅ تم تحميل الإعدادات المحسنة للأداء بنجاح!")
print(f"🔧 وضع التطوير: {'مفعل' if DEBUG else 'معطل'}")
print(f"💾 نوع الكاش: {CACHES['default']['BACKEND'].split('.')[-1]}")
print(f"📊 مراقبة الأداء: {'مفعلة' if PERFORMANCE_MONITORING else 'معطلة'}")
