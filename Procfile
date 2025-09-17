release: cd src && python manage.py migrate && python manage.py collectstatic --noinput
web: cd src && gunicorn project.wsgi:application --bind 0.0.0.0:$PORT --workers 2 --timeout 120
