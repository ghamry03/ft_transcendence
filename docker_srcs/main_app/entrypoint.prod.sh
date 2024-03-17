#!/bin/bash

python manage.py flush --no-input
python manage.py makemigrations
python manage.py migrate --noinput
gunicorn main_app.wsgi:application --bind 0.0.0.0:8000