@echo off
color 0A
echo.
echo ======================================================
echo    فحص المشروع قبل رفعه على GitHub - Pre-Commit Check
echo ======================================================
echo.

set "error_found=0"

REM Check 1: Verify .env file is removed
echo [1/8] فحص ملف .env...
if exist .env (
    echo ❌ خطر! ملف .env موجود - يحتوي على بيانات حساسة
    echo    يجب حذف ملف .env قبل الـ commit
    set "error_found=1"
) else (
    echo ✅ ممتاز! ملف .env محذوف
)

REM Check 2: Verify .env.example exists
echo.
echo [2/8] فحص ملف .env.example...
if exist .env.example (
    echo ✅ ممتاز! ملف .env.example موجود
) else (
    echo ❌ خطأ! ملف .env.example مفقود
    set "error_found=1"
)

REM Check 3: Check for large files
echo.
echo [3/8] فحص الملفات الكبيرة...
if exist cmd.exe (
    echo ❌ خطر! cmd.exe موجود (273MB) - سيرفض GitHub هذا الملف
    set "error_found=1"
) else (
    echo ✅ ممتاز! لا توجد ملفات cmd.exe
)

REM Check 4: Check for virtual environment files
echo.
echo [4/8] فحص ملفات البيئة الافتراضية...
set "venv_found=0"
if exist Scripts\ set "venv_found=1"
if exist Lib\ set "venv_found=1"
if exist Include\ set "venv_found=1"
if exist pyvenv.cfg set "venv_found=1"

if %venv_found%==1 (
    echo ❌ تحذير! ملفات البيئة الافتراضية موجودة
    echo    Scripts/, Lib/, Include/, pyvenv.cfg
    echo    هذه الملفات ستجعل المشروع ثقيل
    set "error_found=1"
) else (
    echo ✅ ممتاز! لا توجد ملفات بيئة افتراضية
)

REM Check 5: Check for database files
echo.
echo [5/8] فحص ملفات قاعدة البيانات...
set "db_found=0"
for /r . %%f in (*.sqlite3) do (
    if exist "%%f" (
        echo ❌ تحذير! ملف قاعدة بيانات موجود: %%f
        set "db_found=1"
    )
)
if %db_found%==0 (
    echo ✅ ممتاز! لا توجد ملفات sqlite3
) else (
    set "error_found=1"
)

REM Check 6: Check for __pycache__ directories
echo.
echo [6/8] فحص مجلدات __pycache__...
set "pycache_found=0"
for /d /r . %%d in (__pycache__) do (
    if exist "%%d" (
        echo ❌ تحذير! مجلد __pycache__ موجود: %%d
        set "pycache_found=1"
    )
)
if %pycache_found%==0 (
    echo ✅ ممتاز! لا توجد مجلدات __pycache__
) else (
    set "error_found=1"
)

REM Check 7: Verify .gitignore exists
echo.
echo [7/8] فحص ملف .gitignore...
if exist .gitignore (
    echo ✅ ممتاز! ملف .gitignore موجود
) else (
    echo ❌ خطأ! ملف .gitignore مفقود
    set "error_found=1"
)

REM Check 8: Verify critical files exist
echo.
echo [8/8] فحص الملفات الأساسية...
set "critical_missing=0"

if not exist README.md (
    echo ❌ README.md مفقود
    set "critical_missing=1"
)

if not exist requirements.txt (
    echo ❌ requirements.txt مفقود في الجذر
    set "critical_missing=1"
)

if not exist src\requirements.txt (
    echo ❌ src\requirements.txt مفقود
    set "critical_missing=1"
)

if %critical_missing%==0 (
    echo ✅ ممتاز! جميع الملفات الأساسية موجودة
) else (
    set "error_found=1"
)

echo.
echo ======================================================
if %error_found%==1 (
    color 0C
    echo    ❌ وُجدت مشاكل! يجب حلها قبل الـ commit
    echo ======================================================
    echo.
    echo الحلول السريعة:
    echo.
    echo لحذف الملفات الكبيرة:
    echo   cleanup_for_git.bat
    echo.
    echo لحذف ملف .env:
    echo   del .env
    echo.
    echo لإنشاء .env.example:
    echo   copy .env .env.example
    echo   [ثم احذف البيانات الحساسة من .env.example]
    echo.
    echo بعد الحلول، شغل هذا السكريبت مرة أخرى
    echo.
) else (
    color 0A
    echo    ✅ رائع! المشروع جاهز للرفع على GitHub
    echo ======================================================
    echo.
    echo الخطوات التالية:
    echo.
    echo 1. git add .
    echo 2. git commit -m "Initial commit: نظام إدارة محلات الحلاقة"
    echo 3. أنشئ repository على GitHub
    echo 4. git remote add origin [repository-url]
    echo 5. git push -u origin main
    echo.
    echo نصائح أمنية:
    echo - لا تنس إنشاء .env جديد للتطوير المحلي
    echo - استخدم .env.example كقالب
    echo - غيّر جميع كلمات المرور في الإنتاج
    echo.
)

echo اضغط أي مفتاح للمتابعة...
pause >nul