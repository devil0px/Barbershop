#!/usr/bin/env python
"""
Startup script for Digital Ocean App Platform
This script helps debug startup issues and provides better error messages
"""
import os
import sys
import django
from django.core.management import execute_from_command_line

def main():
    """Run the Django development server with debugging"""
    print("=== BARBERSHOP STARTUP DEBUG ===")
    print(f"Python version: {sys.version}")
    print(f"Django version: {django.get_version()}")
    print(f"Current working directory: {os.getcwd()}")
    print(f"Python path: {sys.path}")
    print(f"PORT environment variable: {os.environ.get('PORT', 'NOT SET')}")
    
    # Set Django settings module
    os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'project.settings')
    
    try:
        # Try to import Django
        from django.core.management import execute_from_command_line
        print("✓ Django imported successfully")
        
        # Try to setup Django
        django.setup()
        print("✓ Django setup completed")
        
        # Get the port
        port = os.environ.get('PORT', '8000')
        print(f"✓ Starting server on port {port}")
        
        # Start the development server
        sys.argv = ['manage.py', 'runserver', f'0.0.0.0:{port}']
        execute_from_command_line(sys.argv)
        
    except ImportError as exc:
        print(f"✗ Django import error: {exc}")
        raise ImportError(
            "Couldn't import Django. Are you sure it's installed and "
            "available on your PYTHONPATH environment variable? Did you "
            "forget to activate a virtual environment?"
        ) from exc
    except Exception as exc:
        print(f"✗ Startup error: {exc}")
        import traceback
        traceback.print_exc()
        raise

if __name__ == '__main__':
    main()
