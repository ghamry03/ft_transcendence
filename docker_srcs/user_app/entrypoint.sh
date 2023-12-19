#!/bin/bash

python manage.py flush --no-input
python manage.py makemigrations
python manage.py migrate --noinput
python manage.py runserver 0.0.0.0:3000