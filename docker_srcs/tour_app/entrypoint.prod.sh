#!/bin/bash

python manage.py flush --no-input
python manage.py makemigrations tour_game
python manage.py makemigrations
python manage.py migrate --noinput
daphne -b 0.0.0.0 -p 8004 tour_app.asgi:application
