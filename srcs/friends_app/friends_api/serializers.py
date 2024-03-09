from rest_framework import serializers
from friends_api.models import Friend
from user_api.serializers import UserSerializer
from user_api.models import User

class FriendSerializer(serializers.ModelSerializer):
    first_id = UserSerializer(many=False, read_only=True)
    second_id = UserSerializer(many=False, read_only=True)
    class Meta:
        model = Friend
        fields = ['id' , 'first_id', 'second_id', 'relationship']
