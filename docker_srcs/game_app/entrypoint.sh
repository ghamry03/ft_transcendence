#!/bin/bash

python manage.py makemigrations online
python manage.py makemigrations
python manage.py migrate --noinput
python manage.py runserver 0.0.0.0:8003
