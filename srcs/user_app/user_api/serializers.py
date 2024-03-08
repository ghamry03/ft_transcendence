from rest_framework import serializers
from .models import User

class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ['uid', 'username', 'first_name',
                  'last_name', 'campus_name', 'intra_url',
                  'image', 'status']

