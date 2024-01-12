from rest_framework import authentication
from rest_framework import exceptions
import requests


class api_auth(authentication.BaseAuthentication):
    def authenticate(self, request):
        uid = request.META.get('HTTP_X_UID')
        token = request.META.get('HTTP_X_TOKEN')
        # TODO: check if auth type exists ( intra, .. )
        # auth_type = request.META.get('HTTP_X_TYPE')
        if not uid or not token:
            raise exceptions.ParseError('Missing authentication headers')
        self.validate_uid(uid, token)

    def validate_uid(self, uid, token):
        headers = {
            'Authorization': 'Bearer ' + token
        }
        response = requests.get(
                'https://api.intra.42.fr/oauth/token/info',
                headers=headers
        )
        response_json = response.json()
        response_id = response_json.get('resource_owner_id')
        if not response_id:
            raise exceptions.AuthenticationFailed('Invalid token')
        if response_id != int(uid):
            raise exceptions.AuthenticationFailed('Invalid token')
