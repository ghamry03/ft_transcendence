FROM python:3.12.0-bullseye

WORKDIR /home/auth_app
                                                         
COPY requirements.txt ./
RUN apt-get update \
    && apt-get install -y --no-install-recommends postgresql-client \
    && rm -rf /var/lib/apt/lists/*
RUN pip install --no-cache-dir -r requirements.txt

EXPOSE 5000

CMD python manage.py runserver 0.0.0.0:5000

