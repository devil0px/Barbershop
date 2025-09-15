# 💈 نظام إدارة محلات الحلاقة - Barber Shop Management System

نظام شامل لإدارة محلات الحلاقة مطور باستخدام Django مع إمكانيات متقدمة للحجز والتواصل الفوري.

## ✨ الميزات الرئيسية

### 🔐 نظام المستخدمين
- **تسجيل ثنائي النوع**: عملاء وأصحاب محلات
- **تفعيل بالإيميل**: نظام كود 6 أرقام مع رابط احتياطي
- **مصادقة اجتماعية**: تسجيل الدخول عبر Google
- **حماية متقدمة**: نظام أمان متعدد الطبقات

### 🏪 إدارة المحلات
- **معلومات شاملة**: الاسم، الوصف، العنوان، الموقع الجغرافي
- **إعدادات مرنة**: أوقات العمل، أنواع الخدمات، الأسعار
- **نظام الصور**: رفع وعرض صور المحل والخدمات
- **إعدادات متقدمة**: الثيم، الألوان، وسائل التواصل الاجتماعي

### 📅 نظام الحجوزات
- **نظام الدور المتطور**: ترقيم تلقائي لكل يوم
- **حجوزات متعددة الخدمات**: إمكانية حجز عدة خدمات في جلسة واحدة
- **حالات متنوعة**: انتظار، مؤكد، مكتمل، ملغي، لم يحضر
- **مراسلة مباشرة**: محادثة فورية بين العميل وصاحب المحل

### 🔔 الإشعارات والتحديثات
- **WebSocket**: تحديثات فورية للدور وحالة الحجوزات
- **إشعارات متنوعة**: رسائل، تأكيد حجز، تحديث الدور
- **إشعارات المتصفح**: إشعارات خارج التطبيق

### ⭐ التقييمات والمراجعات
- **نظام النجوم**: تقييم من 1 إلى 5 نجوم
- **مراجعات مع صور**: إمكانية رفع صور مع التقييم
- **نظام الموافقة**: تحكم في عرض التقييمات

## 🛠️ التقنيات المستخدمة

- **Backend**: Django 5.2.3, Python
- **Frontend**: Bootstrap 5.3, JavaScript, Arabic RTL
- **Database**: SQLite (قابل للترقية لـ PostgreSQL)
- **Real-time**: Django Channels, WebSocket
- **Authentication**: Django Allauth, Google OAuth
- **File Handling**: Django Media Files, WhiteNoise
- **Security**: CSRF Protection, Custom Middleware

## 🚀 التثبيت والإعداد

### المتطلبات الأساسية
```bash
Python 3.8+
pip
Git
```

### 1. استنساخ المشروع
```bash
git clone https://github.com/your-username/barbershop.git
cd barbershop
```

### 2. إنشاء البيئة الافتراضية
```bash
python -m venv venv
# Windows
venv\Scripts\activate
# Linux/Mac
source venv/bin/activate
```

### 3. تثبيت المتطلبات
```bash
pip install -r requirements.txt
```

### 4. إعداد متغيرات البيئة
```bash
cp .env.example .env
```

قم بتحرير ملف `.env` وأضف قيمك الخاصة:
```env
DEBUG=True
SECRET_KEY=your-very-long-random-secret-key
EMAIL_HOST_USER=your_email@gmail.com
EMAIL_HOST_PASSWORD=your_app_password
GOOGLE_CLIENT_ID=your_google_client_id
GOOGLE_SECRET_KEY=your_google_secret_key
```

### 5. إعداد قاعدة البيانات
```bash
cd src
python manage.py makemigrations
python manage.py migrate
python manage.py createsuperuser
```

### 6. جمع الملفات الثابتة
```bash
python manage.py collectstatic
```

### 7. تشغيل الخادم
```bash
python manage.py runserver
```

الآن يمكنك زيارة: `http://localhost:8000`

## 🔧 إعداد Google OAuth

1. اذهب إلى [Google Cloud Console](https://console.cloud.google.com/)
2. أنشئ مشروعاً جديداً أو استخدم موجود
3. فعّل APIs التالية:
   - Google+ API
   - Google Identity Services API
4. أنشئ OAuth 2.0 Credentials
5. أضف Authorized Origins:
   ```
   http://localhost:8000
   https://yourdomain.com
   ```
6. أضف Redirect URIs:
   ```
   http://localhost:8000/accounts/google/login/callback/
   https://yourdomain.com/accounts/google/login/callback/
   ```
7. انسخ Client ID و Secret إلى ملف `.env`

## 📧 إعداد الإيميل (Gmail)

1. فعّل التحقق بخطوتين على حسابك في Gmail
2. اذهب إلى [App Passwords](https://myaccount.google.com/apppasswords)
3. أنشئ كلمة مرور تطبيق جديدة
4. استخدم كلمة المرور هذه في متغير `EMAIL_HOST_PASSWORD`

## 📁 هيكل المشروع

```
Barbershop/
├── src/                      # الكود الرئيسي
│   ├── accounts/            # نظام المستخدمين
│   ├── barbershops/         # إدارة المحلات
│   ├── bookings/           # نظام الحجوزات
│   ├── reviews/            # التقييمات
│   ├── notifications/      # الإشعارات
│   ├── home/               # الصفحة الرئيسية
│   ├── project/            # إعدادات المشروع
│   ├── templates/          # القوالب
│   ├── static/            # الملفات الثابتة
│   └── media/             # الملفات المرفوعة
├── requirements.txt        # المتطلبات
├── .env.example           # قالب متغيرات البيئة
└── README.md              # هذا الملف
```

## 🔐 الأمان

### الحماية المطبقة:
- **CSRF Protection**: حماية من هجمات CSRF
- **XSS Protection**: فلترة المدخلات
- **SQL Injection**: استخدام Django ORM
- **Admin Security**: مسار إدارة مخفي
- **HTTPS Support**: دعم SSL/TLS
- **Session Security**: أمان الجلسات

### إرشادات الأمان:
- غيّر `SECRET_KEY` في الإنتاج
- استخدم HTTPS في الإنتاج
- فعّل جميع إعدادات الأمان
- راجع ملف `.gitignore` قبل الرفع

## 🚀 النشر في الإنتاج

### متغيرات البيئة المطلوبة:
```env
DEBUG=False
SECRET_KEY=your-production-secret-key
ALLOWED_HOSTS=yourdomain.com,www.yourdomain.com
DATABASE_URL=your-database-url
EMAIL_HOST_USER=production_email@yourdomain.com
EMAIL_HOST_PASSWORD=production_email_password
GOOGLE_CLIENT_ID=production_google_client_id
GOOGLE_SECRET_KEY=production_google_secret_key
```

### خطوات النشر:
1. إعداد قاعدة بيانات الإنتاج (PostgreSQL مُستحسن)
2. تحديث `ALLOWED_HOSTS`
3. جمع الملفات الثابتة: `python manage.py collectstatic`
4. تشغيل التطبيق عبر Gunicorn أو uWSGI
5. إعداد Nginx للملفات الثابتة والوكيل العكسي

## 🐛 استكشاف الأخطاء

### مشاكل شائعة:

#### خطأ في الإيميل:
```
SMTPAuthenticationError
```
**الحل**: تأكد من تفعيل App Password في Gmail

#### خطأ في Google OAuth:
```
Invalid client_id
```
**الحل**: تأكد من صحة Client ID في ملف `.env`

#### خطأ في قاعدة البيانات:
```
OperationalError
```
**الحل**: تأكد من تطبيق Migrations: `python manage.py migrate`

## 📝 المساهمة

1. Fork المشروع
2. أنشئ فرع جديد: `git checkout -b feature/amazing-feature`
3. Commit التغييرات: `git commit -m 'Add amazing feature'`
4. Push للفرع: `git push origin feature/amazing-feature`
5. أنشئ Pull Request

## 📄 الترخيص

هذا المشروع مرخص تحت رخصة MIT - انظر ملف [LICENSE](LICENSE) للتفاصيل.

## 📞 التواصل

- **المطور**: [اسمك]
- **الإيميل**: your.email@example.com
- **LinkedIn**: [ملفك الشخصي]
- **GitHub**: [حسابك على GitHub]

## 🙏 شكر وتقدير

شكر خاص لـ:
- Django Community
- Bootstrap Team  
- Font Awesome
- جميع المطورين الذين ساهموا في المكتبات المستخدمة

---

**ملاحظة مهمة**: تأكد من مراجعة جميع إعدادات الأمان قبل النشر في الإنتاج! 🔐