#!/bin/bash

pip install -r requirements.txt 1> /dev/null
python manage.py runserver
