from rest_framework import serializers
from online.models import Game, Tournament, PlayerMatch

class GameSerializer(serializers.ModelSerializer):
    class Meta:
        model = Game
        fields = ['id', 'starttime', 'endtime', 'tournament']

class TournamentSerializer(serializers.ModelSerializer):
    class Meta:
        model = Tournament
        fields = ['id', 'starttime']

class MatchSerializer(serializers.ModelSerializer):
    class Meta:
        model = PlayerMatch
        fields = ['id', 'game', 'player', 'score']

#modify serializers in order to parse the responses from the api to return only what is required for the game history
# Append to the match history the opponent name and image
# Do not show on the response the ID number or value for the user1, only for user 2 
#
#
#
#
#
#
#
#
#
#
#
#
        