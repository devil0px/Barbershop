#!/usr/bin/env python
"""
Simple test server to verify basic functionality
"""
import os
import sys

def main():
    print("=== BASIC SERVER TEST ===")
    print(f"Python executable: {sys.executable}")
    print(f"Python version: {sys.version}")
    print(f"Current directory: {os.getcwd()}")
    print(f"PORT: {os.environ.get('PORT', 'NOT SET')}")
    
    # Test basic imports
    try:
        import django
        print(f"Django version: {django.get_version()}")
    except ImportError as e:
        print(f"Django import failed: {e}")
        return 1
    
    # Set Django settings
    os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'project.settings')
    
    try:
        django.setup()
        print("Django setup successful")
    except Exception as e:
        print(f"Django setup failed: {e}")
        import traceback
        traceback.print_exc()
        return 1
    
    # Start simple HTTP server
    port = int(os.environ.get('PORT', 8000))
    print(f"Starting server on port {port}")
    
    from django.core.management import execute_from_command_line
    sys.argv = ['manage.py', 'runserver', f'0.0.0.0:{port}', '--insecure']
    execute_from_command_line(sys.argv)

if __name__ == '__main__':
    sys.exit(main())
