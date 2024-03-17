FROM nginx:latest

WORKDIR /etc/nginx/conf.d
RUN [ -f /etc/nginx/conf.d/default.conf ] && rm /etc/nginx/conf.d/default.conf || exit 0
COPY ./conf.d/. /etc/nginx/conf.d/

RUN apt update && apt install ca-certificates -y && apt install nano -y
RUN apt install net-tools iputils-ping -y
RUN openssl req -x509 -nodes -days 365 -newkey rsa:2048 -keyout /etc/ssl/private/nginx-selfsigned.key -out /etc/ssl/certs/nginx-selfsigned.crt \
    -subj "/C=AE/ST=AbuDhabi/L=AbuDhabi/O=42AbuDhabi/OU=./CN=$DOMAIN"
EXPOSE 443
