#!/bin/bash

python manage.py makemigrations user_api
python manage.py makemigrations
python manage.py migrate --noinput
DJANGO_SUPERUSER_USERNAME=$SQL_USER \
DJANGO_SUPERUSER_PASSWORD=$SQL_PASSWORD \
DJANGO_SUPERUSER_EMAIL="admin@admin.com" \
python manage.py createsuperuser --noinput
python manage.py runserver 0.0.0.0:8001