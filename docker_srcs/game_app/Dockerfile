FROM python:3.12.0-bullseye

WORKDIR /home/game_app
                                                         
COPY requirements.txt ./
# RUN pip install virtualenv
# RUN virtualenv venv


# RUN python -m venv django-env
# RUN source venv/bin/activate
RUN apt-get update \
    && apt-get install -y --no-install-recommends postgresql-client \
    && rm -rf /var/lib/apt/lists/*
RUN pip install --no-cache-dir -r requirements.txt

EXPOSE 8003

COPY entrypoint.sh /
RUN chmod a+x /entrypoint.sh
ENTRYPOINT [ "/entrypoint.sh"]

# CMD python manage.py runserver 0.0.0.0:8003
# CMD [ "/bin/bash" ]
