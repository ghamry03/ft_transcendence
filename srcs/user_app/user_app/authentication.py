from rest_framework import authentication
from rest_framework import exceptions
import requests
from user_api.models import User


class api_auth(authentication.BaseAuthentication):
    def authenticate(self, request):
        uid = request.META.get('HTTP_X_UID')
        if not uid:
            raise exceptions.ParseError('Missing authentication header')

        if request.method == 'GET' and self.UserExist(int(uid)):
            pass
        else:
            token = request.META.get('HTTP_X_TOKEN')
            if not token:
                raise exceptions.ParseError('Missing authentication headers')
            self.validate_uid(uid, token)

    def UserExist(self, requested_uid):
        try:
            User.objects.get(uid=requested_uid)
        except User.DoesNotExist:
            return False
        return True

    def validate_uid(self, uid, token):
        headers = {
            'Authorization': 'Bearer ' + token
        }
        response = requests.get(
                'https://api.intra.42.fr/oauth/token/info',
                headers=headers
        )
        if response.status_code != 200:
            raise exceptions.AuthenticationFailed('Failed to connect to intra')
        response_json = response.json()
        response_id = response_json.get('resource_owner_id')
        if not response_id:
            raise exceptions.AuthenticationFailed('Invalid token')
        if response_id != int(uid):
            raise exceptions.AuthenticationFailed('Invalid token')
