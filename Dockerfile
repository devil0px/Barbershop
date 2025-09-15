# استخدام Python 3.11 كصورة أساسية
FROM python:3.11-slim

# تعيين متغيرات البيئة
ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1
ENV DEBIAN_FRONTEND=noninteractive

# تعيين مجلد العمل
WORKDIR /app

# تثبيت متطلبات النظام
RUN apt-get update \
    && apt-get install -y --no-install-recommends \
        postgresql-client \
        build-essential \
        libpq-dev \
        gettext \
        nginx \
        supervisor \
    && rm -rf /var/lib/apt/lists/*

# نسخ متطلبات Python وتثبيتها
COPY requirements.txt /app/
RUN pip install --no-cache-dir -r requirements.txt

# نسخ كود المشروع
COPY . /app/

# نسخ ملفات الإعداد
COPY docker/nginx.conf /etc/nginx/sites-available/default
COPY docker/supervisord.conf /etc/supervisor/conf.d/supervisord.conf

# إنشاء مجلدات مطلوبة
RUN mkdir -p /app/staticfiles /app/media /var/log/supervisor

# تعيين الصلاحيات
RUN chmod +x docker/entrypoint.sh

# تجميع الملفات الثابتة
RUN cd src && python manage.py collectstatic --noinput

# فتح المنافذ
EXPOSE 80 8000

# نقطة الدخول
ENTRYPOINT ["./docker/entrypoint.sh"]
