# ⚡ النشر السريع على DigitalOcean

## 🎯 خطوات سريعة (5 دقائق)

### 1. إنشاء التطبيق
1. اذهب إلى: https://cloud.digitalocean.com/apps
2. انقر "Create App"
3. اختر GitHub → `devil0px/Barbershop` → `main` branch
4. تفعيل "Autodeploy"

### 2. إعداد المتغيرات (مطلوب!)
```env
SECRET_KEY=django-insecure-CHANGE-THIS-TO-RANDOM-50-CHARS
EMAIL_HOST_USER=your-email@gmail.com
EMAIL_HOST_PASSWORD=your-gmail-app-password
GOOGLE_CLIENT_ID=your-google-client-id
GOOGLE_SECRET_KEY=your-google-secret-key
```

### 3. إضافة قواعد البيانات
- PostgreSQL 15 (Basic - $7/month)
- Redis 7 (Basic - $7/month)

### 4. النشر
- انقر "Create Resources"
- انتظر 5-10 دقائق
- احصل على الرابط: `https://your-app.ondigitalocean.app`

## 🔑 الحصول على المتغيرات

### SECRET_KEY:
```python
import secrets
print(secrets.token_urlsafe(50))
```

### Gmail App Password:
1. تفعيل 2FA على Gmail
2. https://myaccount.google.com/apppasswords
3. إنشاء كلمة مرور جديدة

### Google OAuth:
1. https://console.cloud.google.com/
2. إنشاء مشروع جديد
3. تفعيل Google+ API
4. إنشاء OAuth 2.0 credentials
5. إضافة redirect URI: `https://your-app.ondigitalocean.app/accounts/google/login/callback/`

## ✅ اختبار سريع
- [ ] فتح الموقع
- [ ] تسجيل حساب جديد
- [ ] تسجيل دخول بـ Google
- [ ] إنشاء محل حلاقة
- [ ] حجز موعد

## 💰 التكلفة
- Web Service: $5/month
- PostgreSQL: $7/month
- Redis: $7/month
- **المجموع: $19/month**

---
**🚀 مبروك! تطبيقك الآن على الإنترنت!**
