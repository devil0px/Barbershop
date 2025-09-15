release: cd src && python manage.py migrate --noinput && python manage.py collectstatic --noinput
web: cd src && gunicorn project.wsgi:application --bind 0.0.0.0:$PORT --workers 1 --timeout 120 --log-level info --access-logfile -
