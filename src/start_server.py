#!/usr/bin/env python
"""
Simple server starter for DigitalOcean deployment
"""
import os
import sys
import django
from django.core.management import execute_from_command_line
from django.core.wsgi import get_wsgi_application

def main():
    """Start the Django server"""
    print("Starting Django server...", flush=True)
    
    # Set Django settings
    os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'project.settings')
    
    try:
        # Setup Django
        django.setup()
        print("Django setup complete", flush=True)
        
        # Get port from environment
        port = os.environ.get('PORT', '8080')
        print(f"Starting server on port {port}", flush=True)
        
        # Run server
        execute_from_command_line([
            'manage.py',
            'runserver',
            f'0.0.0.0:{port}'
        ])
        
    except Exception as e:
        print(f"Error starting server: {e}", flush=True)
        import traceback
        traceback.print_exc()
        return 1
    
    return 0

if __name__ == '__main__':
    sys.exit(main())
