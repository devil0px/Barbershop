# إعداد GitHub Secrets للنشر التلقائي

لإعداد النشر التلقائي على Digital Ocean، تحتاج لإضافة المتغيرات التالية في GitHub Secrets:

## كيفية إضافة GitHub Secrets:

1. اذهب إلى مستودع GitHub الخاص بك
2. اضغط على **Settings**
3. من القائمة الجانبية، اختر **Secrets and variables** > **Actions**
4. اضغط على **New repository secret**

## المتغيرات المطلوبة:

### معلومات الخادم
```
DO_HOST=your-server-ip-address
DO_USERNAME=barbershop
DO_SSH_KEY=your-private-ssh-key-content
DO_PORT=22
```

### متغيرات قاعدة البيانات
```
POSTGRES_DB=barbershop
POSTGRES_USER=barbershop_user
POSTGRES_PASSWORD=your_secure_password
```

### إعدادات Django
```
SECRET_KEY=your-super-long-random-secret-key-at-least-50-characters
ALLOWED_HOSTS=your-domain.com,www.your-domain.com
CSRF_TRUSTED_ORIGINS=https://your-domain.com,https://www.your-domain.com
```

### إعدادات الإيميل
```
EMAIL_HOST_USER=noreply@your-domain.com
EMAIL_HOST_PASSWORD=your_email_app_password
DEFAULT_FROM_EMAIL=Barber Shop <noreply@your-domain.com>
```

### Google OAuth
```
GOOGLE_CLIENT_ID=your_google_client_id
GOOGLE_SECRET_KEY=your_google_secret_key
```

### Redis
```
REDIS_URL=redis://redis:6379/1
```

## خطوات إضافية:

### 1. إنشاء SSH Key للخادم:
```bash
# على جهازك المحلي
ssh-keygen -t rsa -b 4096 -c "github-actions@your-domain.com"

# انسخ المفتاح العام إلى الخادم
ssh-copy-id -i ~/.ssh/id_rsa.pub barbershop@your-server-ip

# انسخ المفتاح الخاص إلى GitHub Secret باسم DO_SSH_KEY
cat ~/.ssh/id_rsa
```

### 2. تحديث اسم المستودع في GitHub Actions:
في ملف `.github/workflows/deploy.yml`، قم بتحديث:
```yaml
env:
  REGISTRY: ghcr.io
  IMAGE_NAME: your-username/barbershop  # غيّر هذا لاسم مستودعك
```

### 3. إنشاء Personal Access Token:
1. اذهب إلى GitHub Settings > Developer settings > Personal access tokens
2. أنشئ token جديد مع صلاحيات `write:packages`
3. أضفه كـ Secret باسم `GITHUB_TOKEN` (أو استخدم الـ token الافتراضي)

## اختبار النشر:

بعد إعداد جميع المتغيرات:

1. ادفع الكود إلى فرع `main`
2. راقب تقدم GitHub Actions في تبويب **Actions**
3. تأكد من نجاح جميع المراحل: Test → Build → Deploy

## استكشاف الأخطاء:

### إذا فشل الاتصال بالخادم:
- تأكد من صحة `DO_HOST` و `DO_USERNAME`
- تأكد من أن SSH Key صحيح ومضاف للخادم
- تأكد من أن المنفذ `DO_PORT` صحيح (عادة 22)

### إذا فشل بناء Docker:
- تأكد من أن جميع الملفات موجودة في المستودع
- تأكد من صحة `Dockerfile` و `requirements.txt`

### إذا فشل النشر:
- تأكد من تثبيت Docker و Docker Compose على الخادم
- تأكد من وجود مجلد `/opt/barbershop` على الخادم
- تأكد من صلاحيات المستخدم `barbershop`
