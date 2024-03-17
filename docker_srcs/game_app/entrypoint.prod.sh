#!/bin/bash

python manage.py flush --no-input
python manage.py makemigrations online
python manage.py makemigrations
python manage.py migrate --noinput
daphne -b 0.0.0.0 -p 8003 game_app.asgi:application
