#!/bin/bash
python manage.py migrate

python manage.py import_ingredients

python manage.py collectstatic --clear
cp -r /app/collected_static/. /backend_static/static/

gunicorn --bind 0.0.0.0:8000 backend.wsgi
