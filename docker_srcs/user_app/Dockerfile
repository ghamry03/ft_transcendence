FROM python:3.12.0-bullseye


# RUN mkdir -p /home/ft_transcendence
WORKDIR /home/user_app


COPY requirements.txt ./
# RUN pip install virtualenv
# RUN virtualenv venv


# RUN python -m venv django-env
# RUN source venv/bin/activate
RUN pip install --no-cache-dir -r requirements.txt
# RUN django-admin startproject mysite

EXPOSE 8001

# COPY . .

# CMD python3 manage.py makemigrations && python3 manage.py migrate

# CMD [ "python", "./your-daemon-or-script.py" ]
COPY entrypoint.sh /
RUN chmod a+x /entrypoint.sh
ENTRYPOINT [ "/entrypoint.sh"]
