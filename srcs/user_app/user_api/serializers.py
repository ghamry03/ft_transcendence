from rest_framework import serializers
from django.conf import settings
from .models import User
from user_app.constants import *

class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = '__all__'

    def to_representation(self, instance):
        representation = super().to_representation(instance)
        request = self.context.get('request')

        if instance.image:
            image_url = instance.image.url
            image_url = MEDIA_SERVICE_URL + image_url
            representation['image'] = image_url
        return representation
