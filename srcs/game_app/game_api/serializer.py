from rest_framework import serializers
from online.models import Game, Tournament, PlayerMatch

class GameSerializer(serializers.ModelSerializer):
    class Meta:
        model = Game
        fields = ['gid', 'startTime', 'endTime', 'tid']

class TournamentSerializer(serializers.ModelSerializer):
    class Meta:
        model = Tournament
        fields = ['tid', 'startTime']

class MatchSerializer(serializers.ModelSerializer):
    class Meta:
        model = PlayerMatch
        fields = ['gid', 'pid', 'score']