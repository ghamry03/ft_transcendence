from main_app.settings import DEBUG
from os import environ

if DEBUG == True:
    AUTH_URL = environ.get('AUTH_URL', 'https://api.intra.42.fr/oauth/authorize?client_id=u-s4t2ud-9c64ddc1254a330959e05ab254676bd2839aaf33ceba357b53462f7f6bb8c345&redirect_uri=http%3A%2F%2F127.0.0.1%3A8000%2Fauthenticate%2F&response_type=code')
    REDIRECT_URI = environ.get('REDIRECT_URI', 'http://127.0.0.1:8000/authenticate/')
    MEDIA_SERVICE_URL = environ.get('MEDIA_URL', 'http://localhost:8001/')
    USER_API_URL = environ.get('USER_API_URL', 'http://userapp:8001/')
    FRIEND_API_URL = environ.get('FRIENDS_API_URL', 'http://friendsapp:8002/')
    MATCH_HISOTRY_URL = environ.get('GAME_API_URL', 'http://gameapp:8003/')
    TOURNAMENT_HISOTRY_URL = environ.get('TOUR_API_URL', 'http://tourapp:8004/')
else:
    AUTH_URL = environ.get('AUTH_URL', 'https://api.intra.42.fr/oauth/authorize?client_id=u-s4t2ud-9c64ddc1254a330959e05ab254676bd2839aaf33ceba357b53462f7f6bb8c345&redirect_uri=https%3A%2F%2Flocalhost%2Fauthenticate%2F&response_type=code')
    REDIRECT_URI = environ.get('REDIRECT_URI', 'https://localhost/authenticate/')
    USER_API_URL = environ.get('USER_API_URL', 'http://userapp:8001/')
    FRIEND_API_URL = environ.get('FRIENDS_API_URL', 'http://friendsapp:8002/')
    MATCH_HISOTRY_URL = environ.get('GAME_API_URL', 'http://gameapp:8003/')
    TOURNAMENT_HISOTRY_URL = environ.get('TOUR_API_URL', 'http://tourapp:8004/')
    MEDIA_SERVICE_URL = environ.get('MEDIA_URL', 'https://localhost:8005/')
