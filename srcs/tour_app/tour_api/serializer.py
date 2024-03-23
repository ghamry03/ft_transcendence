from rest_framework import serializers
from tour_game.models import Tournament, OnlineGame, OnlinePlayermatch, UserApiUser


class GameSerializer(serializers.ModelSerializer):
    class Meta:
        model = OnlineGame
        fields = ['id', 'starttime', 'endtime', 'tournament']

class TournamentSerializer(serializers.ModelSerializer):
    class Meta:
        model = Tournament
        fields = ['id', 'starttime']

class MatchSerializer(serializers.ModelSerializer):
    class Meta:
        model = OnlinePlayermatch
        fields = ['score', 'game', 'player']

class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = UserApiUser
        fields = ['uid', 'username', 'first_name', 'image', 'status']
