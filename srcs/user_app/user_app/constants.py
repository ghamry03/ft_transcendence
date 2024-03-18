from user_app.settings import DEBUG

if DEBUG == True:
    MEDIA_SERVICE_URL = 'http://localhost:8001'
    FRIEND_API_URL = 'http://friendsapp:8002/'
else:
    MEDIA_SERVICE_URL = 'https://localhost:8005'
    FRIEND_API_URL = 'https://friendsapp:8002/'
