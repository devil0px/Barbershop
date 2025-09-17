# 🔧 إصلاحات مشاكل النشر الشائعة

## 🚨 خطأ "Non-Zero Exit Code" - الحلول

### ✅ الإصلاحات المطبقة:

#### 1. إصلاح مسار requirements.txt
- ✅ نقل requirements.txt للجذر
- ✅ تحديث build_command في app.yaml
- ✅ إضافة dj-database-url

#### 2. إصلاح run_command
- ✅ دمج الأوامر في سطر واحد
- ✅ استخدام && بدلاً من أسطر منفصلة

#### 3. إعدادات Django مؤقتة للتشخيص
- ✅ تفعيل DEBUG=True مؤقتاً
- ✅ إضافة '*' في ALLOWED_HOSTS مؤقتاً

## 🔍 خطوات التشخيص:

### 1. تحقق من متغيرات البيئة المطلوبة:
```env
SECRET_KEY=your-secret-key-here
DATABASE_URL=${db.DATABASE_URL}
REDIS_URL=${redis.REDIS_URL}
```

### 2. تحقق من قواعد البيانات:
- ✅ PostgreSQL database اسمه "db"
- ✅ Redis database اسمه "redis"

### 3. تحقق من الأوامر:
```bash
# Build Command:
pip install -r requirements.txt

# Run Command:
cd src && python manage.py collectstatic --noinput && python manage.py migrate --noinput && gunicorn project.wsgi:application --bind 0.0.0.0:$PORT --workers 2 --timeout 120
```

## 🚀 خطوات إعادة النشر:

### 1. تأكد من وجود قواعد البيانات:
- PostgreSQL (اسم: db)
- Redis (اسم: redis)

### 2. تأكد من متغيرات البيئة:
- SECRET_KEY (مطلوب)
- DEBUG=True (مؤقت للتشخيص)

### 3. أعد النشر:
- Git push سيؤدي لنشر تلقائي
- أو انقر "Deploy" في لوحة التحكم

## 🔧 مشاكل شائعة أخرى:

### مشكلة: Database Connection Error
```bash
# الحل:
- تأكد من إنشاء PostgreSQL database
- تأكد من اسم database هو "db"
- تأكد من متغير DATABASE_URL
```

### مشكلة: Static Files Error
```bash
# الحل:
- تأكد من تشغيل collectstatic
- تأكد من وجود مجلد staticfiles
```

### مشكلة: Import Error
```bash
# الحل:
- تأكد من صحة requirements.txt
- تأكد من Python version (3.11.9)
```

## 📋 قائمة فحص سريعة:

- [ ] requirements.txt في الجذر ✅
- [ ] PostgreSQL database موجود
- [ ] Redis database موجود  
- [ ] SECRET_KEY متغير موجود
- [ ] DEBUG=True (مؤقت)
- [ ] ALLOWED_HOSTS يحتوي على '*'
- [ ] Build command صحيح
- [ ] Run command صحيح

## 🎯 بعد حل المشكلة:

### إعادة الإعدادات الآمنة:
```yaml
- key: DEBUG
  value: "False"
```

```python
ALLOWED_HOSTS = ['.ondigitalocean.app']  # إزالة '*'
```

---
**💡 نصيحة: راجع الـ logs في DigitalOcean لمعرفة الخطأ الدقيق!**
