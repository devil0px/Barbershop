# 🚀 دليل النشر التلقائي على Digital Ocean

تم إعداد نظام نشر تلقائي شامل لمشروع Barbershop على Digital Ocean باستخدام Docker و GitHub Actions.

## 📋 الملفات المُنشأة

### ملفات Docker
- `Dockerfile` - صورة Docker للتطبيق
- `docker-compose.yml` - إعداد التطوير المحلي
- `docker/entrypoint.sh` - سكريبت بدء التطبيق
- `docker/nginx.conf` - إعدادات Nginx
- `docker/supervisord.conf` - إدارة العمليات

### ملفات CI/CD
- `.github/workflows/deploy.yml` - GitHub Actions للنشر التلقائي
- `deploy/github_secrets_setup.md` - دليل إعداد GitHub Secrets

### ملفات الخادم
- `deploy/digital_ocean_setup.sh` - سكريبت إعداد الخادم
- `.env.production` - متغيرات البيئة للإنتاج

## 🛠️ خطوات النشر

### 1. إعداد Digital Ocean Droplet

```bash
# إنشاء Droplet جديد (Ubuntu 22.04)
# تشغيل سكريبت الإعداد كـ root
wget https://raw.githubusercontent.com/your-username/barbershop/main/deploy/digital_ocean_setup.sh
chmod +x digital_ocean_setup.sh
./digital_ocean_setup.sh
```

### 2. إعداد GitHub Repository

1. ادفع الكود إلى GitHub
2. أضف GitHub Secrets (راجع `deploy/github_secrets_setup.md`)
3. فعّل GitHub Actions

### 3. إعداد متغيرات البيئة

```bash
# على الخادم
cd /opt/barbershop
cp .env.example .env
nano .env  # عدّل القيم المطلوبة
```

### 4. بدء النشر التلقائي

```bash
# ادفع إلى فرع main لبدء النشر
git push origin main
```

## 🔧 الميزات المُضافة

### Docker Multi-Stage Build
- صورة محسّنة للإنتاج
- تشغيل Nginx + Django في حاوية واحدة
- دعم WebSocket للتحديثات الفورية

### CI/CD Pipeline
- اختبار تلقائي قبل النشر
- بناء ونشر صور Docker
- نشر تلقائي على Digital Ocean
- إشعارات حالة النشر

### أمان محسّن
- SSL/HTTPS إجباري
- Firewall مُعد مسبقاً
- Fail2Ban للحماية من الهجمات
- إعدادات أمان Nginx متقدمة

### مراقبة ونسخ احتياطي
- نسخ احتياطي يومي تلقائي لقاعدة البيانات
- مراقبة الخدمات عبر Supervisor
- سجلات مفصلة لجميع الخدمات

## 📊 بنية النشر

```
Digital Ocean Droplet
├── Nginx (Port 80/443)
│   ├── SSL Termination
│   ├── Static Files Serving
│   └── Reverse Proxy to Django
├── Django App (Port 8000)
│   ├── Gunicorn WSGI Server
│   └── Daphne ASGI Server (WebSocket)
├── PostgreSQL Database
└── Redis Cache
```

## 🔍 مراقبة النشر

### عرض حالة الخدمات
```bash
cd /opt/barbershop
docker-compose -f docker-compose.prod.yml ps
```

### عرض السجلات
```bash
# جميع الخدمات
docker-compose -f docker-compose.prod.yml logs -f

# خدمة محددة
docker-compose -f docker-compose.prod.yml logs -f web
```

### إعادة النشر يدوياً
```bash
cd /opt/barbershop
./deploy.sh
```

## 🆘 استكشاف الأخطاء

### مشاكل شائعة وحلولها

#### 1. فشل الاتصال بقاعدة البيانات
```bash
# فحص حالة PostgreSQL
docker-compose -f docker-compose.prod.yml logs db

# إعادة تشغيل قاعدة البيانات
docker-compose -f docker-compose.prod.yml restart db
```

#### 2. مشاكل SSL
```bash
# فحص شهادة SSL
openssl x509 -in /opt/barbershop/ssl/cert.pem -text -noout

# تجديد شهادة Let's Encrypt
certbot renew
```

#### 3. مشاكل الذاكرة
```bash
# فحص استخدام الذاكرة
docker stats

# إعادة تشغيل الخدمات
docker-compose -f docker-compose.prod.yml restart
```

## 📈 تحسينات مستقبلية

### مقترحات للتطوير
- [ ] إضافة مراقبة Prometheus + Grafana
- [ ] إعداد CDN للملفات الثابتة
- [ ] تحسين أداء قاعدة البيانات
- [ ] إضافة Load Balancer للتوسع الأفقي
- [ ] تطبيق Blue-Green Deployment

### أمان إضافي
- [ ] إعداد WAF (Web Application Firewall)
- [ ] مراقبة الأمان مع Fail2Ban المتقدم
- [ ] تشفير قاعدة البيانات
- [ ] إعداد VPN للوصول الإداري

## 📞 الدعم

في حالة مواجهة مشاكل:

1. راجع السجلات أولاً
2. تأكد من إعدادات متغيرات البيئة
3. فحص حالة الخدمات
4. راجع دليل استكشاف الأخطاء

---

**🎉 مبروك! مشروعك الآن يدعم النشر التلقائي على Digital Ocean**
