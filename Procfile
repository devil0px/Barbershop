release: python manage.py collectstatic --noinput
web: gunicorn project.wsgi:application --log-file - --log-level debug
