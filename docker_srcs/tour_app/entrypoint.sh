#!/bin/bash

python manage.py flush --no-input
python manage.py makemigrations tour_game
python manage.py makemigrations
python manage.py migrate --noinput
python manage.py runserver 0.0.0.0:8004
# daphne tour_app.asgi:application --bind 0.0.0.0:8004
