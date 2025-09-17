# 🌊 دليل النشر على DigitalOcean App Platform

## 🚀 خطوات النشر السريع

### 1. إنشاء التطبيق على DigitalOcean

1. **اذهب إلى**: [DigitalOcean App Platform](https://cloud.digitalocean.com/apps)
2. **انقر على**: "Create App"
3. **اختر**: "GitHub" كمصدر
4. **اختر Repository**: `devil0px/Barbershop`
5. **اختر Branch**: `main`
6. **تفعيل**: "Autodeploy" لنشر تلقائي عند كل push

### 2. إعداد التطبيق

#### الإعدادات الأساسية:
- **App Name**: `barbershop-management-system`
- **Region**: اختر الأقرب لك (Frankfurt, New York, etc.)
- **Plan**: Basic ($5/month) أو Professional ($12/month)

#### إعدادات الخدمة:
- **Service Type**: Web Service
- **Source Directory**: `/` (الجذر)
- **Build Command**: سيتم تحديده تلقائياً من `app.yaml`
- **Run Command**: سيتم تحديده تلقائياً من `app.yaml`

### 3. إعداد قواعد البيانات

#### PostgreSQL Database:
- **Name**: `db`
- **Engine**: PostgreSQL 15
- **Plan**: Basic ($7/month)

#### Redis Database:
- **Name**: `redis`
- **Engine**: Redis 7
- **Plan**: Basic ($7/month)

### 4. متغيرات البيئة المطلوبة

#### متغيرات إجبارية:
```env
SECRET_KEY=your-super-long-random-secret-key-here
EMAIL_HOST_USER=your-email@gmail.com
EMAIL_HOST_PASSWORD=your-gmail-app-password
GOOGLE_CLIENT_ID=your-google-oauth-client-id
GOOGLE_SECRET_KEY=your-google-oauth-secret-key
```

#### متغيرات اختيارية:
```env
DEFAULT_FROM_EMAIL=Barber Shop <noreply@yourdomain.com>
SITE_DOMAIN=your-custom-domain.com
```

### 5. إعداد Google OAuth

1. **اذهب إلى**: [Google Cloud Console](https://console.cloud.google.com/)
2. **أنشئ مشروع جديد** أو استخدم موجود
3. **فعّل APIs**:
   - Google+ API
   - Google Identity Services API
4. **أنشئ OAuth 2.0 Credentials**
5. **أضف Authorized Origins**:
   ```
   https://your-app-name.ondigitalocean.app
   https://your-custom-domain.com (إذا كان لديك نطاق مخصص)
   ```
6. **أضف Redirect URIs**:
   ```
   https://your-app-name.ondigitalocean.app/accounts/google/login/callback/
   ```

### 6. إعداد Gmail للإيميلات

1. **فعّل التحقق بخطوتين** على حساب Gmail
2. **اذهب إلى**: [App Passwords](https://myaccount.google.com/apppasswords)
3. **أنشئ كلمة مرور تطبيق جديدة**
4. **استخدم كلمة المرور** في `EMAIL_HOST_PASSWORD`

## 🔧 خطوات النشر التفصيلية

### الخطوة 1: إنشاء التطبيق
```bash
# لا حاجة لأوامر - كل شيء عبر واجهة الويب
```

### الخطوة 2: ربط GitHub Repository
- Repository: `https://github.com/devil0px/Barbershop`
- Branch: `main`
- Auto Deploy: ✅ مفعل

### الخطوة 3: إعداد المتغيرات
في لوحة التحكم، اذهب إلى Settings > Environment Variables:

#### متغيرات SECRET (مخفية):
- `SECRET_KEY`: مفتاح Django السري
- `EMAIL_HOST_USER`: إيميل Gmail
- `EMAIL_HOST_PASSWORD`: كلمة مرور التطبيق
- `GOOGLE_CLIENT_ID`: معرف Google OAuth
- `GOOGLE_SECRET_KEY`: مفتاح Google OAuth السري

#### متغيرات عادية:
- `DEBUG`: `False`
- `ALLOWED_HOSTS`: `.ondigitalocean.app`
- `DEFAULT_FROM_EMAIL`: `Barber Shop <noreply@yourdomain.com>`

### الخطوة 4: إعداد قواعد البيانات
1. **أضف PostgreSQL Database**:
   - Name: `db`
   - Version: 15
   - Size: Basic

2. **أضف Redis Database**:
   - Name: `redis`
   - Version: 7
   - Size: Basic

### الخطوة 5: النشر
- انقر على "Create Resources"
- انتظر اكتمال البناء (5-10 دقائق)
- ستحصل على رابط مثل: `https://barbershop-management-system-xxxxx.ondigitalocean.app`

## 🎯 ما بعد النشر

### 1. اختبار التطبيق
- ✅ تسجيل الدخول/إنشاء حساب
- ✅ Google OAuth
- ✅ إرسال الإيميلات
- ✅ رفع الصور
- ✅ الإشعارات الفورية

### 2. إعداد النطاق المخصص (اختياري)
1. **في لوحة التحكم**: Settings > Domains
2. **أضف نطاقك**: `yourdomain.com`
3. **أضف CNAME Record** في إعدادات النطاق:
   ```
   CNAME @ barbershop-management-system-xxxxx.ondigitalocean.app
   ```

### 3. إعداد SSL
- SSL مجاني ومفعل تلقائياً
- يتم تجديده تلقائياً

## 💰 التكلفة المتوقعة

### الحد الأدنى (Basic):
- **Web Service**: $5/شهر
- **PostgreSQL**: $7/شهر  
- **Redis**: $7/شهر
- **المجموع**: ~$19/شهر

### المُوصى به (Professional):
- **Web Service**: $12/شهر
- **PostgreSQL**: $15/شهر
- **Redis**: $15/شهر
- **المجموع**: ~$42/شهر

## 🔍 مراقبة التطبيق

### Logs والتشخيص:
- **Runtime Logs**: في لوحة التحكم > Runtime Logs
- **Build Logs**: في لوحة التحكم > Activity
- **Metrics**: CPU, Memory, Network usage

### تنبيهات:
- إعداد تنبيهات للأخطاء
- مراقبة استخدام الموارد
- تنبيهات وقت التوقف

## 🆘 حل المشاكل الشائعة

### مشكلة: Build Failed
```bash
# تحقق من:
- صحة requirements.txt
- وجود ملف manage.py في src/
- صحة إعدادات Python version
```

### مشكلة: Database Connection Error
```bash
# تحقق من:
- إعداد DATABASE_URL صحيح
- قاعدة البيانات تعمل
- Migrations تم تطبيقها
```

### مشكلة: Static Files لا تظهر
```bash
# تحقق من:
- تم تشغيل collectstatic
- إعدادات STATIC_ROOT صحيحة
- WhiteNoise مثبت
```

## 📞 الدعم

- **DigitalOcean Docs**: [App Platform Documentation](https://docs.digitalocean.com/products/app-platform/)
- **Community**: [DigitalOcean Community](https://www.digitalocean.com/community/)
- **Support**: [DigitalOcean Support](https://cloud.digitalocean.com/support)

---

**🎉 مبروك! تطبيق إدارة محلات الحلاقة الآن يعمل على DigitalOcean! 🎉**
