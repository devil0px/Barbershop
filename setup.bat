@echo off
echo ========================================
echo       اعداد نظام Barber Shop
echo ========================================
echo.

echo تشغيل الترحيلات...
python manage.py migrate

echo.
echo انشاء السوبر يوزر واعداد البيانات الاولية...
python setup_admin.py

echo.
echo فحص التطبيقات المسجلة...
python check_admin_apps.py

echo.
echo ========================================
echo         تم الانتهاء من الاعداد
echo ========================================
echo.
echo يمكنك الان تشغيل الخادم باستخدام:
echo python manage.py runserver
echo.
pause