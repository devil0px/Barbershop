#!/usr/bin/env python
import os
import sys

# Add current directory to Python path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

# Set Django settings
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'project.settings')

# Simple server start
if __name__ == '__main__':
    try:
        from django.core.management import execute_from_command_line
        
        port = os.environ.get('PORT', '8080')
        print(f"Starting Django server on port {port}")
        
        # Run migrations first
        execute_from_command_line(['manage.py', 'migrate', '--noinput'])
        print("Migrations completed")
        
        # Collect static files
        execute_from_command_line(['manage.py', 'collectstatic', '--noinput'])
        print("Static files collected")
        
        # Start server
        execute_from_command_line(['manage.py', 'runserver', f'0.0.0.0:{port}'])
        
    except Exception as e:
        print(f"Error: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)
