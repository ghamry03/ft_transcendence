from user_app.settings import DEBUG
from os import environ

if DEBUG == True:
    MEDIA_SERVICE_URL = environ.get('MEDIA_URL', 'http://localhost:8001/')
    FRIEND_API_URL = environ.get('FRIENDS_API_URL', 'http://friendsapp:8002/')
else:
    MEDIA_SERVICE_URL = environ.get('MEDIA_URL', 'https://localhost:8005/')
    FRIEND_API_URL = environ.get('FRIENDS_API_URL', 'http://friendsapp:8002/')
