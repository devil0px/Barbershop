release: cd src && python manage.py migrate --noinput && python manage.py collectstatic --noinput
web: cd src && python -m gunicorn wsgi --bind 0.0.0.0:$PORT --workers 1 --timeout 120 --log-level info --access-logfile - --error-logfile -
