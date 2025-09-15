release: cd src && python manage.py migrate --noinput && python manage.py collectstatic --noinput
web: cd src && gunicorn --config gunicorn_config.py project.wsgi:application
