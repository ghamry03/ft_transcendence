import requests
from rest_framework import serializers
from friends_api.models import Friend
from django.db import connections
from django.core.exceptions import ValidationError
from . import USER_API_URL

import logging

logger = logging.getLogger(__name__)

class FriendSerializer(serializers.ModelSerializer):
    # first_id = UserSerializer(many=False)
    # second_id = UserSerializer(many=False)
    class Meta:
        model = Friend
        fields = ['id' , 'first_id', 'second_id', 'relationship']

    def validate(self, data):
        first_id = data.get('first_id')
        second_id = data.get('second_id')

        if Friend.objects.filter(first_id=first_id, second_id=second_id).exists():
            raise serializers.ValidationError("the two users are already Friends", code='duplicate')

        if Friend.objects.filter(first_id=second_id, second_id=first_id).exists():
            raise serializers.ValidationError("the two users are already Friends", code='duplicate')

        return data
    
    def validate_user_id(self, user_id):
        headers = {
            'X-UID': self.context.get('requester_uid', None),
            'X-TOKEN': self.context.get('access_token', None)
        }

        base_url = f"{USER_API_URL}users/api/{user_id}/"
        
        response = requests.get(base_url, headers=headers)
        if response.status_code != 200:
            raise serializers.ValidationError(f"User with ID {user_id} does not exist.", code='dne')
        return user_id

    def validate_first_id(self, value):
        if not self.validate_user_id(value):
            raise serializers.ValidationError("First user does not exist.", code='dne')
        return value

    def validate_second_id(self, value):
        if not self.validate_user_id(value):
            raise serializers.ValidationError("Second user does not exist.", code='dne')
        return value
