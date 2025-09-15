# 🚀 دليل النشر في الإنتاج - Production Deployment Guide

## ⚠️ تحذيرات مهمة قبل النشر

### 🔐 إعدادات الأمان الإجبارية

#### 1. متغيرات البيئة الآمنة
```env
# .env للإنتاج
DEBUG=False
SECRET_KEY=your-super-long-random-secret-key-at-least-50-characters-long
ALLOWED_HOSTS=yourdomain.com,www.yourdomain.com,api.yourdomain.com

# قاعدة البيانات - استخدم PostgreSQL
DATABASE_URL=postgres://user:password@host:port/database_name

# الإيميل - استخدم خدمة احترافية
EMAIL_HOST_USER=noreply@yourdomain.com
EMAIL_HOST_PASSWORD=your_email_service_password
DEFAULT_FROM_EMAIL=Barber Shop <noreply@yourdomain.com>

# Google OAuth - إعدادات الإنتاج
GOOGLE_CLIENT_ID=your_production_google_client_id
GOOGLE_SECRET_KEY=your_production_google_secret_key

# إعدادات إضافية للإنتاج
SECURE_SSL_REDIRECT=True
SESSION_COOKIE_SECURE=True
CSRF_COOKIE_SECURE=True
```

#### 2. توليد SECRET_KEY آمن
```python
# في Python shell
import secrets
secret_key = secrets.token_urlsafe(50)
print(f"SECRET_KEY={secret_key}")
```

### 🗄️ قاعدة البيانات

#### التحديث من SQLite إلى PostgreSQL:
```bash
# 1. تثبيت PostgreSQL driver
pip install psycopg2-binary

# 2. تحديث settings.py
DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.postgresql',
        'NAME': env('DB_NAME'),
        'USER': env('DB_USER'),
        'PASSWORD': env('DB_PASSWORD'),
        'HOST': env('DB_HOST', default='localhost'),
        'PORT': env('DB_PORT', default='5432'),
    }
}

# أو استخدم DATABASE_URL
import dj_database_url
DATABASES = {
    'default': dj_database_url.parse(env('DATABASE_URL'))
}
```

### 🌐 خدمات النشر المُوصى بها

#### 1. Heroku (سهل للمبتدئين)
```bash
# 1. تثبيت Heroku CLI
# 2. إنشاء Procfile
echo "web: gunicorn project.wsgi" > Procfile

# 3. تحديث requirements.txt
pip freeze > requirements.txt

# 4. النشر
heroku create your-app-name
heroku config:set DEBUG=False
heroku config:set SECRET_KEY=your-secret-key
git push heroku main
```

#### 2. DigitalOcean App Platform
```yaml
# .do/app.yaml
name: barbershop-app
services:
- name: web
  source_dir: /
  github:
    repo: your-username/barbershop
    branch: main
  run_command: gunicorn --worker-tmp-dir /dev/shm project.wsgi
  environment_slug: python
  instance_count: 1
  instance_size_slug: basic-xxs
  envs:
  - key: DEBUG
    value: "False"
  - key: SECRET_KEY
    value: "your-secret-key"
```

#### 3. Railway (بديل Heroku)
```bash
# 1. تثبيت Railway CLI
# 2. النشر
railway login
railway init
railway add
railway deploy
```

### 📦 إعداد الخادم (VPS)

#### متطلبات النظام:
```bash
# Ubuntu 20.04+ أو CentOS 8+
sudo apt update
sudo apt install python3 python3-pip nginx postgresql redis-server
```

#### إعداد Gunicorn:
```bash
# gunicorn.conf.py
bind = "0.0.0.0:8000"
workers = 2
worker_class = "gevent"
worker_connections = 1000
max_requests = 1000
max_requests_jitter = 100
timeout = 30
keepalive = 2
```

#### إعداد Nginx:
```nginx
# /etc/nginx/sites-available/barbershop
server {
    listen 80;
    server_name yourdomain.com www.yourdomain.com;
    return 301 https://$server_name$request_uri;
}

server {
    listen 443 ssl http2;
    server_name yourdomain.com www.yourdomain.com;
    
    ssl_certificate /path/to/your/cert.pem;
    ssl_certificate_key /path/to/your/private.key;
    
    location / {
        proxy_pass http://127.0.0.1:8000;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
    }
    
    location /static/ {
        alias /path/to/your/staticfiles/;
        expires 1y;
        add_header Cache-Control "public, immutable";
    }
    
    location /media/ {
        alias /path/to/your/media/;
        expires 1y;
        add_header Cache-Control "public, immutable";
    }
}
```

### 🔄 CI/CD مع GitHub Actions

#### `.github/workflows/deploy.yml`:
```yaml
name: Deploy to Production

on:
  push:
    branches: [ main ]

jobs:
  deploy:
    runs-on: ubuntu-latest
    
    steps:
    - uses: actions/checkout@v2
    
    - name: Set up Python
      uses: actions/setup-python@v2
      with:
        python-version: 3.9
    
    - name: Install dependencies
      run: |
        pip install -r requirements.txt
    
    - name: Run tests
      run: |
        python src/manage.py test
    
    - name: Deploy to Heroku
      uses: akhileshns/heroku-deploy@v3.12.12
      with:
        heroku_api_key: ${{secrets.HEROKU_API_KEY}}
        heroku_app_name: "your-app-name"
        heroku_email: "your-email@example.com"
```

### 📊 المراقبة والتحليل

#### Sentry (مراقبة الأخطاء):
```python
# settings.py
import sentry_sdk
from sentry_sdk.integrations.django import DjangoIntegration

sentry_sdk.init(
    dsn=env('SENTRY_DSN'),
    integrations=[DjangoIntegration()],
    traces_sample_rate=0.1,
    send_default_pii=True
)
```

### 🔒 النسخ الاحتياطي

#### نسخ احتياطي يومي:
```bash
#!/bin/bash
# backup.sh
DATE=$(date +%Y%m%d_%H%M%S)
pg_dump $DATABASE_URL > /backups/db_$DATE.sql
aws s3 cp /backups/db_$DATE.sql s3://your-backup-bucket/
```

### 📈 تحسين الأداء

#### Redis للتخزين المؤقت:
```python
# settings.py
CACHES = {
    "default": {
        "BACKEND": "django_redis.cache.RedisCache",
        "LOCATION": env('REDIS_URL', default='redis://localhost:6379/1'),
        "OPTIONS": {
            "CLIENT_CLASS": "django_redis.client.DefaultClient",
        }
    }
}

SESSION_ENGINE = "django.contrib.sessions.backends.cache"
SESSION_CACHE_ALIAS = "default"
```

#### CDN للملفات الثابتة:
```python
# للملفات الثابتة عبر AWS CloudFront
STATICFILES_STORAGE = 'whitenoise.storage.CompressedManifestStaticFilesStorage'
DEFAULT_FILE_STORAGE = 'storages.backends.s3boto3.S3Boto3Storage'

AWS_ACCESS_KEY_ID = env('AWS_ACCESS_KEY_ID')
AWS_SECRET_ACCESS_KEY = env('AWS_SECRET_ACCESS_KEY')
AWS_STORAGE_BUCKET_NAME = env('AWS_STORAGE_BUCKET_NAME')
```

## ✅ قائمة فحص ما قبل النشر

- [ ] تم تعيين `DEBUG=False`
- [ ] تم توليد `SECRET_KEY` جديد وآمن
- [ ] تم تحديث `ALLOWED_HOSTS`
- [ ] تم إعداد قاعدة بيانات الإنتاج
- [ ] تم اختبار Google OAuth مع النطاق الجديد
- [ ] تم إعداد SSL/HTTPS
- [ ] تم تشغيل `collectstatic`
- [ ] تم اختبار جميع الوظائف
- [ ] تم إعداد النسخ الاحتياطي
- [ ] تم إعداد مراقبة الأخطاء

## 🆘 حل مشاكل النشر الشائعة

### خطأ: "DisallowedHost"
```python
# تأكد من إضافة النطاق في ALLOWED_HOSTS
ALLOWED_HOSTS = ['yourdomain.com', 'www.yourdomain.com']
```

### خطأ: "CSRF verification failed"
```python
# تأكد من إضافة النطاق في CSRF_TRUSTED_ORIGINS
CSRF_TRUSTED_ORIGINS = [
    'https://yourdomain.com',
    'https://www.yourdomain.com',
]
```

### خطأ: الملفات الثابتة لا تظهر
```bash
# تأكد من تشغيل collectstatic
python manage.py collectstatic --noinput
```

---

**⚠️ تذكر: لا تنشر أبداً مع `DEBUG=True` في الإنتاج!**