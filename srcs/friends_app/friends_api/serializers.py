from rest_framework import serializers
from friends_api.models import Friend, RELATIONSHIP_CHOICE

class FriendSerializer(serializers.ModelSerializer):
    class Meta:
        model = Friend
        fields = ['id' , 'first_id', 'second_id', 'relationship']