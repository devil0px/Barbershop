release: cd src && python manage.py collectstatic --noinput && python manage.py migrate
web: cd src && gunicorn project.wsgi:application --bind 0.0.0.0:$PORT --log-file - --log-level info
worker: cd src && daphne -b 0.0.0.0 -p $PORT project.asgi:application
