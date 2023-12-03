FROM python:3.12.0-bullseye


# RUN mkdir -p /home/ft_transcendence
WORKDIR /home/main_app


COPY requirements.txt ./
# RUN pip install virtualenv
# RUN virtualenv venv


# RUN python -m venv django-env
# RUN source venv/bin/activate
RUN pip install --no-cache-dir -r requirements.txt
# RUN django-admin startproject mysite


# COPY . .


# CMD [ "python", "./your-daemon-or-script.py" ]
# COPY entrypoint.sh /
# RUN chmod a+x /entrypoint.sh
# ENTRYPOINT [ "/entrypoint.sh"]


EXPOSE 8000
CMD python manage.py runserver 0.0.0.0:8000
# CMD [ "/bin/bash" ]
