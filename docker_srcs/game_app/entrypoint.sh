#!/bin/bash

python manage.py flush --no-input
python manage.py makemigrations online
python manage.py makemigrations
python manage.py migrate --noinput
python manage.py runserver 0.0.0.0:2000
# daphne game_app.asgi:application --bind 0.0.0.0:2000
# export DJANGO_SETTINGS_MODULE='game_app.settings'
# echo "Starting Daphne server"
# daphne -b 0.0.0.0 -p 2000 game_app.asgi:application
