from rest_framework import serializers
from online.models import Game, TourGameTournament, PlayerMatch

class GameSerializer(serializers.ModelSerializer):
    class Meta:
        model = Game
        fields = ['id', 'starttime', 'endtime', 'tournament']

class TournamentSerializer(serializers.ModelSerializer):
    class Meta:
        model = TourGameTournament
        fields = ['id', 'starttime']

class MatchSerializer(serializers.ModelSerializer):
    class Meta:
        model = PlayerMatch
        fields = ['id', 'game', 'player', 'score']

        