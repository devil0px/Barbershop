#!/usr/bin/env python3
"""
سكريبت لحل مشكلة قفل قاعدة البيانات SQLite
Database Unlock Script for SQLite lock issues
"""

import sqlite3
import os
import sys
import time

def unlock_database():
    """فتح قفل قاعدة البيانات"""
    db_path = 'db.sqlite3'
    
    if not os.path.exists(db_path):
        print("[ERROR] ملف قاعدة البيانات غير موجود!")
        return False
    
    try:
        print("[INFO] محاولة فتح قفل قاعدة البيانات...")
        
        # محاولة الاتصال بقاعدة البيانات
        conn = sqlite3.connect(db_path, timeout=30)
        cursor = conn.cursor()
        
        # تشغيل استعلام بسيط للتأكد من عمل قاعدة البيانات
        cursor.execute("SELECT name FROM sqlite_master WHERE type='table' LIMIT 1;")
        result = cursor.fetchone()
        
        # إغلاق الاتصال
        cursor.close()
        conn.close()
        
        print("[OK] تم فتح قفل قاعدة البيانات بنجاح!")
        print(f"[DATA] قاعدة البيانات تحتوي على جداول: {result}")
        return True
        
    except sqlite3.OperationalError as e:
        if "database is locked" in str(e):
            print("[LOCKED] قاعدة البيانات ما زالت مقفلة!")
            print("[TIP] جرب الحلول التالية:")
            print("   1. أغلق جميع نوافذ المتصفح")
            print("   2. أوقف جميع عمليات Python")
            print("   3. أعد تشغيل الكمبيوتر إذا لزم الأمر")
            return False
        else:
            print(f"[ERROR] خطأ في قاعدة البيانات: {e}")
            return False
    except Exception as e:
        print(f"[ERROR] خطأ غير متوقع: {e}")
        return False

def check_running_processes():
    """فحص العمليات الجارية"""
    print("[CHECK] فحص العمليات الجارية...")
    
    try:
        import psutil
        python_processes = []
        
        for proc in psutil.process_iter(['pid', 'name', 'cmdline']):
            try:
                if proc.info['name'] and 'python' in proc.info['name'].lower():
                    cmdline = ' '.join(proc.info['cmdline']) if proc.info['cmdline'] else ''
                    if 'manage.py' in cmdline or 'runserver' in cmdline:
                        python_processes.append({
                            'pid': proc.info['pid'],
                            'cmdline': cmdline
                        })
            except (psutil.NoSuchProcess, psutil.AccessDenied):
                continue
        
        if python_processes:
            print("[WARNING]  عمليات Django جارية:")
            for proc in python_processes:
                print(f"   PID: {proc['pid']} - {proc['cmdline']}")
            print("[TIP] أوقف هذه العمليات أولاً!")
        else:
            print("[OK] لا توجد عمليات Django جارية")
            
    except ImportError:
        print("[NOTE] لا يمكن فحص العمليات (psutil غير مثبت)")

if __name__ == "__main__":
    print("=" * 50)
    print("اداة حل مشكلة قفل قاعدة البيانات")
    print("=" * 50)
    
    # فحص العمليات الجارية
    check_running_processes()
    print()
    
    # محاولة فتح القفل
    success = unlock_database()
    
    if success:
        print("\n[SUCCESS] يمكنك الآن تشغيل Django بأمان!")
        print("[RUN]  python manage.py runserver")
    else:
        print("\n[RETRY] إذا استمرت المشكلة:")
        print("   1. أعد تشغيل الكمبيوتر")
        print("   2. أو احذف ملف db.sqlite3 واستخدم النسخة الاحتياطية")
        print("   3. أو أنشئ قاعدة بيانات جديدة")
