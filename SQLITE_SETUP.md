# 🗃️ إعداد SQLite للنشر المؤقت

## 🎯 الهدف:
استخدام SQLite بدلاً من PostgreSQL لتجنب تكلفة قاعدة البيانات الخارجية مؤقتاً.

## ✅ التغييرات المطبقة:

### 1. إعدادات قاعدة البيانات:
```python
# استخدام SQLite كافتراضي
DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.sqlite3',
        'NAME': BASE_DIR / 'db.sqlite3',
        'OPTIONS': {
            'timeout': 20,
        }
    }
}
```

### 2. إعدادات Channels:
```python
# استخدام InMemory بدلاً من Redis
CHANNEL_LAYERS = {
    "default": {
        "BACKEND": "channels.layers.InMemoryChannelLayer"
    }
}
```

### 3. app.yaml مبسط:
- ✅ إزالة PostgreSQL database
- ✅ إزالة Redis database  
- ✅ تعليق متغيرات DATABASE_URL و REDIS_URL

### 4. requirements.txt:
- ✅ تعليق psycopg2-binary (غير مطلوب مع SQLite)

## 💰 توفير التكلفة:
- **PostgreSQL**: $7/شهر → $0
- **Redis**: $7/شهر → $0
- **المجموع المحفوظ**: $14/شهر

## ⚠️ قيود SQLite في الإنتاج:

### المحدوديات:
- ❌ لا يدعم الكتابة المتزامنة من عدة workers
- ❌ ملف قاعدة البيانات قد يُفقد عند إعادة النشر
- ❌ أداء أقل مع البيانات الكبيرة

### الحلول المؤقتة:
- ✅ استخدام worker واحد فقط
- ✅ نسخ احتياطي دوري للبيانات
- ✅ ترقية لـ PostgreSQL لاحقاً

## 🔄 للترقية لـ PostgreSQL لاحقاً:

### 1. إضافة PostgreSQL في app.yaml:
```yaml
databases:
- name: db
  engine: PG
  version: "15"
  size: basic
```

### 2. إضافة متغير البيئة:
```yaml
- key: DATABASE_URL
  value: "${db.DATABASE_URL}"
```

### 3. إلغاء تعليق psycopg2-binary:
```txt
psycopg2-binary==2.9.9
```

## 🚀 النشر الحالي:
- **التكلفة**: $5/شهر فقط (Web Service)
- **قاعدة البيانات**: SQLite (مجاني)
- **Channels**: InMemory (مجاني)

---
**💡 هذا الإعداد مثالي للاختبار والتطوير، وقابل للترقية لاحقاً!**
