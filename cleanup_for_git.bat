@echo off
echo تنظيف المشروع قبل رفعه على GitHub...
echo.

echo إزالة الملفات الكبيرة وغير الضرورية...
if exist cmd.exe (
    del cmd.exe
    echo تم حذف cmd.exe
)

if exist pyvenv.cfg (
    del pyvenv.cfg  
    echo تم حذف pyvenv.cfg
)

if exist Scripts (
    rmdir /s /q Scripts
    echo تم حذف مجلد Scripts
)

if exist Lib (
    rmdir /s /q Lib
    echo تم حذف مجلد Lib
)

if exist Include (
    rmdir /s /q Include
    echo تم حذف مجلد Include
)

echo.
echo البحث عن ملفات __pycache__...
for /d /r . %%d in (__pycache__) do @if exist "%%d" rd /s /q "%%d" && echo تم حذف: %%d

echo.
echo البحث عن ملفات .sqlite3...
for /r . %%f in (*.sqlite3) do @if exist "%%f" del "%%f" && echo تم حذف: %%f

echo.
echo البحث عن ملفات .log...
for /r . %%f in (*.log) do @if exist "%%f" del "%%f" && echo تم حذف: %%f

echo.
echo تم الانتهاء من التنظيف!
echo.
echo الخطوات التالية:
echo 1. تأكد من تحديث ملف .env بقيمك الخاصة
echo 2. احذف ملف .env الحالي قبل الـ commit
echo 3. تشغيل: git init
echo 4. تشغيل: git add .
echo 5. تشغيل: git commit -m "Initial commit: نظام إدارة محلات الحلاقة"
echo 6. إنشاء repository على GitHub
echo 7. تشغيل: git remote add origin https://github.com/username/repo.git
echo 8. تشغيل: git push -u origin main
echo.
pause