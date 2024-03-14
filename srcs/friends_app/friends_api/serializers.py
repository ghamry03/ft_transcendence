from rest_framework import serializers
from friends_api.models import Friend
from django.db import connections
from django.core.exceptions import ValidationError
from user_api.serializers import UserSerializer
from user_api.models import User

class FriendSerializer(serializers.ModelSerializer):
    first_id = UserSerializer(many=False)
    second_id = UserSerializer(many=False)
    class Meta:
        model = Friend
        fields = ['id' , 'first_id', 'second_id', 'relationship']

    def validate_first_id(self, value):
        with connections['users'].cursor() as cursor:
            cursor.execute("SELECT COUNT(*) FROM user_api_user WHERE uid = %s", [value])
            if cursor.fetchone()[0] == 0:
                raise serializers.ValidationError("First user does not exists")
        return value

    def validate_second_id(self, value):
        with connections['users'].cursor() as cursor:
            cursor.execute("SELECT COUNT(*) FROM user_api_user WHERE uid = %s", [value])
            if cursor.fetchone()[0] == 0:
                raise serializers.ValidationError("Second user does not exists")
        return value
