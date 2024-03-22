from main_app.settings import DEBUG

if DEBUG == True:
    AUTH_URL = 'https://api.intra.42.fr/oauth/authorize?client_id=u-s4t2ud-997a9b10994157fcd0f6626e52473dc45ef17c7b0b4461694653cd045b01d222&redirect_uri=http%3A%2F%2F127.0.0.1%3A8000%2Fauthenticate%2F&response_type=code'
    REDIRECT_URI = 'http://127.0.0.1:8000/authenticate/'
    MEDIA_SERVICE_URL = 'http://localhost:8001/'
    USER_API_URL = 'http://userapp:8001/'
    FRIEND_API_URL = 'http://friendsapp:8002/'
    TOURNAMENT_HISOTRY_URL = 'http://tourapp:8004/'
else:
    AUTH_URL = 'https://api.intra.42.fr/oauth/authorize?client_id=u-s4t2ud-9c64ddc1254a330959e05ab254676bd2839aaf33ceba357b53462f7f6bb8c345&redirect_uri=https%3A%2F%2Flocalhost%2Fauthenticate%2F&response_type=code'
    REDIRECT_URI = 'https://localhost/authenticate/'
    MEDIA_SERVICE_URL = 'https://localhost:8005'
    USER_API_URL = 'http://userapp:8001/'
    FRIEND_API_URL = 'http://friendsapp:8002/'
    TOURNAMENT_HISOTRY_URL = 'http://tourapp:8004/'
