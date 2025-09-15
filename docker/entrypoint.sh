#!/bin/bash

# انتظار قاعدة البيانات
echo "انتظار قاعدة البيانات..."
while ! nc -z db 5432; do
  sleep 0.1
done
echo "قاعدة البيانات جاهزة!"

# الانتقال لمجلد المشروع
cd /app/src

# تطبيق migrations
echo "تطبيق migrations..."
python manage.py migrate --noinput

# إنشاء superuser إذا لم يكن موجود
echo "إنشاء superuser..."
python manage.py shell << EOF
from django.contrib.auth import get_user_model
User = get_user_model()
if not User.objects.filter(is_superuser=True).exists():
    User.objects.create_superuser('admin', 'admin@example.com', 'admin123')
    print('تم إنشاء superuser: admin/admin123')
else:
    print('superuser موجود بالفعل')
EOF

# تجميع الملفات الثابتة
echo "تجميع الملفات الثابتة..."
python manage.py collectstatic --noinput

# بدء supervisor
echo "بدء الخدمات..."
exec supervisord -c /etc/supervisor/conf.d/supervisord.conf
