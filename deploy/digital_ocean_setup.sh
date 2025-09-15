#!/bin/bash

# سكريبت إعداد Digital Ocean Droplet لمشروع Barbershop
# يجب تشغيله كـ root على Ubuntu 22.04

set -e

echo "🚀 بدء إعداد خادم Digital Ocean للمشروع..."

# تحديث النظام
echo "📦 تحديث النظام..."
apt update && apt upgrade -y

# تثبيت المتطلبات الأساسية
echo "🔧 تثبيت المتطلبات الأساسية..."
apt install -y \
    curl \
    wget \
    git \
    nginx \
    ufw \
    fail2ban \
    htop \
    unzip \
    software-properties-common \
    apt-transport-https \
    ca-certificates \
    gnupg \
    lsb-release

# تثبيت Docker
echo "🐳 تثبيت Docker..."
curl -fsSL https://download.docker.com/linux/ubuntu/gpg | gpg --dearmor -o /usr/share/keyrings/docker-archive-keyring.gpg
echo "deb [arch=$(dpkg --print-architecture) signed-by=/usr/share/keyrings/docker-archive-keyring.gpg] https://download.docker.com/linux/ubuntu $(lsb_release -cs) stable" | tee /etc/apt/sources.list.d/docker.list > /dev/null
apt update
apt install -y docker-ce docker-ce-cli containerd.io

# تثبيت Docker Compose
echo "🔧 تثبيت Docker Compose..."
curl -L "https://github.com/docker/compose/releases/latest/download/docker-compose-$(uname -s)-$(uname -m)" -o /usr/local/bin/docker-compose
chmod +x /usr/local/bin/docker-compose

# إنشاء مستخدم للمشروع
echo "👤 إنشاء مستخدم المشروع..."
useradd -m -s /bin/bash barbershop
usermod -aG docker barbershop
usermod -aG sudo barbershop

# إنشاء مجلد المشروع
echo "📁 إنشاء مجلد المشروع..."
mkdir -p /opt/barbershop
chown barbershop:barbershop /opt/barbershop

# إعداد SSH للمستخدم الجديد
echo "🔑 إعداد SSH..."
mkdir -p /home/barbershop/.ssh
cp /root/.ssh/authorized_keys /home/barbershop/.ssh/
chown -R barbershop:barbershop /home/barbershop/.ssh
chmod 700 /home/barbershop/.ssh
chmod 600 /home/barbershop/.ssh/authorized_keys

# إعداد Firewall
echo "🔥 إعداد Firewall..."
ufw default deny incoming
ufw default allow outgoing
ufw allow ssh
ufw allow 80/tcp
ufw allow 443/tcp
ufw --force enable

# إعداد Fail2Ban
echo "🛡️ إعداد Fail2Ban..."
systemctl enable fail2ban
systemctl start fail2ban

# إنشاء ملف docker-compose للإنتاج
echo "📝 إنشاء ملف docker-compose للإنتاج..."
cat > /opt/barbershop/docker-compose.prod.yml << 'EOF'
version: '3.8'

services:
  db:
    image: postgres:15
    restart: always
    volumes:
      - postgres_data:/var/lib/postgresql/data/
    environment:
      POSTGRES_DB: ${POSTGRES_DB}
      POSTGRES_USER: ${POSTGRES_USER}
      POSTGRES_PASSWORD: ${POSTGRES_PASSWORD}
    networks:
      - barbershop_network

  redis:
    image: redis:7-alpine
    restart: always
    command: redis-server --appendonly yes
    volumes:
      - redis_data:/data
    networks:
      - barbershop_network

  web:
    image: ghcr.io/your-username/barbershop:latest
    restart: always
    volumes:
      - static_volume:/app/staticfiles
      - media_volume:/app/media
    environment:
      - DEBUG=False
      - DATABASE_URL=postgres://${POSTGRES_USER}:${POSTGRES_PASSWORD}@db:5432/${POSTGRES_DB}
      - REDIS_URL=redis://redis:6379/1
      - SECRET_KEY=${SECRET_KEY}
      - ALLOWED_HOSTS=${ALLOWED_HOSTS}
      - CSRF_TRUSTED_ORIGINS=${CSRF_TRUSTED_ORIGINS}
      - EMAIL_HOST_USER=${EMAIL_HOST_USER}
      - EMAIL_HOST_PASSWORD=${EMAIL_HOST_PASSWORD}
      - GOOGLE_CLIENT_ID=${GOOGLE_CLIENT_ID}
      - GOOGLE_SECRET_KEY=${GOOGLE_SECRET_KEY}
    depends_on:
      - db
      - redis
    networks:
      - barbershop_network

  nginx:
    image: nginx:alpine
    restart: always
    ports:
      - "80:80"
      - "443:443"
    volumes:
      - ./nginx/nginx.conf:/etc/nginx/conf.d/default.conf
      - static_volume:/app/staticfiles
      - media_volume:/app/media
      - ./ssl:/etc/nginx/ssl
    depends_on:
      - web
    networks:
      - barbershop_network

volumes:
  postgres_data:
  redis_data:
  static_volume:
  media_volume:

networks:
  barbershop_network:
    driver: bridge
EOF

# إنشاء ملف البيئة النموذجي
echo "🔧 إنشاء ملف البيئة النموذجي..."
cat > /opt/barbershop/.env.example << 'EOF'
# قاعدة البيانات
POSTGRES_DB=barbershop
POSTGRES_USER=barbershop_user
POSTGRES_PASSWORD=your_secure_password_here

# Django
SECRET_KEY=your-super-long-random-secret-key-at-least-50-characters-long
DEBUG=False
ALLOWED_HOSTS=your-domain.com,www.your-domain.com
CSRF_TRUSTED_ORIGINS=https://your-domain.com,https://www.your-domain.com

# الإيميل
EMAIL_HOST_USER=noreply@your-domain.com
EMAIL_HOST_PASSWORD=your_email_password
DEFAULT_FROM_EMAIL=Barber Shop <noreply@your-domain.com>

# Google OAuth
GOOGLE_CLIENT_ID=your_google_client_id
GOOGLE_SECRET_KEY=your_google_secret_key

# Redis
REDIS_URL=redis://redis:6379/1
EOF

# إنشاء سكريبت النشر
echo "🚀 إنشاء سكريبت النشر..."
cat > /opt/barbershop/deploy.sh << 'EOF'
#!/bin/bash

set -e

echo "🚀 بدء عملية النشر..."

# التأكد من وجود ملف البيئة
if [ ! -f .env ]; then
    echo "❌ ملف .env غير موجود! يرجى إنشاؤه من .env.example"
    exit 1
fi

# سحب آخر التحديثات
echo "📥 سحب آخر التحديثات..."
git pull origin main

# سحب الصورة الجديدة
echo "🐳 سحب الصورة الجديدة..."
docker-compose -f docker-compose.prod.yml pull

# إيقاف الخدمات القديمة
echo "⏹️ إيقاف الخدمات القديمة..."
docker-compose -f docker-compose.prod.yml down

# بدء الخدمات الجديدة
echo "▶️ بدء الخدمات الجديدة..."
docker-compose -f docker-compose.prod.yml up -d

# انتظار بدء الخدمات
echo "⏳ انتظار بدء الخدمات..."
sleep 30

# فحص حالة الخدمات
echo "🔍 فحص حالة الخدمات..."
docker-compose -f docker-compose.prod.yml ps

# تنظيف الصور القديمة
echo "🧹 تنظيف الصور القديمة..."
docker image prune -f

echo "✅ تم النشر بنجاح!"
EOF

chmod +x /opt/barbershop/deploy.sh

# إنشاء مجلد nginx
mkdir -p /opt/barbershop/nginx

# إنشاء إعدادات nginx للإنتاج
cat > /opt/barbershop/nginx/nginx.conf << 'EOF'
upstream django {
    server web:8000;
}

# إعادة توجيه HTTP إلى HTTPS
server {
    listen 80;
    server_name _;
    return 301 https://$host$request_uri;
}

server {
    listen 443 ssl http2;
    server_name your-domain.com www.your-domain.com;
    
    # إعدادات SSL
    ssl_certificate /etc/nginx/ssl/cert.pem;
    ssl_certificate_key /etc/nginx/ssl/key.pem;
    
    # إعدادات SSL محسّنة
    ssl_protocols TLSv1.2 TLSv1.3;
    ssl_ciphers ECDHE-RSA-AES256-GCM-SHA512:DHE-RSA-AES256-GCM-SHA512:ECDHE-RSA-AES256-GCM-SHA384:DHE-RSA-AES256-GCM-SHA384;
    ssl_prefer_server_ciphers off;
    ssl_session_cache shared:SSL:10m;
    ssl_session_timeout 10m;
    
    # إعدادات الأمان
    add_header Strict-Transport-Security "max-age=31536000; includeSubDomains" always;
    add_header X-Frame-Options "SAMEORIGIN" always;
    add_header X-Content-Type-Options "nosniff" always;
    add_header Referrer-Policy "no-referrer-when-downgrade" always;
    add_header Content-Security-Policy "default-src 'self' http: https: data: blob: 'unsafe-inline'" always;
    
    # الحد الأقصى لحجم الملف المرفوع
    client_max_body_size 50M;
    
    location / {
        proxy_pass http://django;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
        proxy_redirect off;
        
        # WebSocket support
        proxy_http_version 1.1;
        proxy_set_header Upgrade $http_upgrade;
        proxy_set_header Connection "upgrade";
        
        # Timeouts
        proxy_connect_timeout 60s;
        proxy_send_timeout 60s;
        proxy_read_timeout 60s;
    }
    
    location /static/ {
        alias /app/staticfiles/;
        expires 1y;
        add_header Cache-Control "public, immutable";
        add_header Access-Control-Allow-Origin "*";
    }
    
    location /media/ {
        alias /app/media/;
        expires 1y;
        add_header Cache-Control "public, immutable";
        add_header Access-Control-Allow-Origin "*";
    }
    
    # Gzip compression
    gzip on;
    gzip_vary on;
    gzip_min_length 1024;
    gzip_proxied expired no-cache no-store private must-revalidate auth;
    gzip_types text/plain text/css text/xml text/javascript application/x-javascript application/xml+rss application/javascript;
}
EOF

# تعيين الصلاحيات
chown -R barbershop:barbershop /opt/barbershop

# إنشاء systemd service للنسخ الاحتياطي
echo "💾 إعداد النسخ الاحتياطي التلقائي..."
cat > /etc/systemd/system/barbershop-backup.service << 'EOF'
[Unit]
Description=Barbershop Database Backup
After=docker.service

[Service]
Type=oneshot
User=barbershop
WorkingDirectory=/opt/barbershop
ExecStart=/bin/bash -c 'docker-compose -f docker-compose.prod.yml exec -T db pg_dump -U $POSTGRES_USER $POSTGRES_DB | gzip > /opt/barbershop/backups/backup_$(date +\%Y\%m\%d_\%H\%M\%S).sql.gz'
EOF

cat > /etc/systemd/system/barbershop-backup.timer << 'EOF'
[Unit]
Description=Run Barbershop backup daily
Requires=barbershop-backup.service

[Timer]
OnCalendar=daily
Persistent=true

[Install]
WantedBy=timers.target
EOF

# إنشاء مجلد النسخ الاحتياطي
mkdir -p /opt/barbershop/backups
chown barbershop:barbershop /opt/barbershop/backups

# تفعيل خدمة النسخ الاحتياطي
systemctl enable barbershop-backup.timer
systemctl start barbershop-backup.timer

echo "✅ تم إعداد الخادم بنجاح!"
echo ""
echo "📋 الخطوات التالية:"
echo "1. انسخ ملف .env.example إلى .env وقم بتعديل القيم"
echo "2. احصل على شهادة SSL (Let's Encrypt أو Cloudflare)"
echo "3. قم بإعداد GitHub Secrets للـ CI/CD"
echo "4. ادفع الكود إلى GitHub لبدء النشر التلقائي"
echo ""
echo "🔧 أوامر مفيدة:"
echo "- عرض حالة الخدمات: docker-compose -f docker-compose.prod.yml ps"
echo "- عرض السجلات: docker-compose -f docker-compose.prod.yml logs -f"
echo "- إعادة تشغيل: ./deploy.sh"
echo ""
echo "🎉 الخادم جاهز للاستخدام!"
