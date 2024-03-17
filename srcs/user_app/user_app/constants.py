from user_app.settings import DEBUG

if DEBUG == True:
    MEDIA_SERVICE_URL = 'http://localhost:8001'
else:
    MEDIA_SERVICE_URL = 'https://localhost:8005'
