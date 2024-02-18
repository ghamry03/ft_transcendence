from django.http import Http404, JsonResponse

from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
import requests
from online.models import PlayerMatch, Game
from game_api.serializer import MatchSerializer, GameSerializer

# List view of all Matches for a given User and his scores
class UserMatchListApiView(APIView):
    def get(self, request, player):
        matches = PlayerMatch.objects.filter(player = player)
        serializer = MatchSerializer(matches, many=True)
        print("")
        return Response(serializer.data, status=status.HTTP_200_OK)

# List view of all Games for a given Tournament
class TournamentGameListApiView(APIView):
    def get(self, request, id):
        games = Game.objects.filter(id=id)
        serializer = GameSerializer(games, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)

# List all players in a given match
class MatchPlayerListApiView(APIView):
    def get(self, request, gid):
        players = PlayerMatch.objects.filter(game=gid)
        serializer = MatchSerializer(players, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)

def health_check(request):
    return JsonResponse({'status': 'ok'})

# game history expected info
# {
#     gameId,
#     myScore,
#     opponentScore
#     opponentName,
#     opponentImageUrl,
#     timePassed // might be in days or hours
# }

# def getPlayerImage(request):
#     ownerUid = request.GET.get('ownerUid')
#     targetUid = request.GET.get('targetUid')
#     token = request.GET.get('token')
#     print("getimage: uid = ", ownerUid, "token = ", token)
#     headers = {
#         'X-UID': ownerUid,
#         'X-TOKEN': token
#     }
#     opponentInfo = requests.get('http://userapp:3000/users/api/' + targetUid, headers=headers)
#     imageUrl = opponentInfo.json()['image']
#     return imageUrl    