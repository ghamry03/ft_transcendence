from datetime  import datetime
from django.http import JsonResponse
from django.utils import timezone
import requests

from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework import status
import logging

from tour_game.models import Tournament, OnlineGame, OnlinePlayermatch, TournamentRank
from tour_api.serializer import GameSerializer, UserSerializer

logger = logging.getLogger(__name__)

def calculate_time_passed(game_endtime):
    def format_time_difference(time_difference):
        if time_difference.days >= 1:
            unit = "day"
            quantity = time_difference.days
        elif time_difference.seconds >= 3600:
            unit = "hour"
            quantity = time_difference.seconds // 3600
        elif time_difference.seconds >= 60:
            unit = "minute"
            quantity = time_difference.seconds // 60
        else:
            unit = "second"
            quantity = time_difference.seconds
        return f"{quantity} {unit}{'s' if quantity > 1 else ''}"

    current_time = datetime.now(timezone.utc)
    time_difference = current_time - game_endtime
    return format_time_difference(time_difference)

def get_rank(user_id, tournament_id):
    try:
        tournament = TournamentRank.objects.get(tournament=tournament_id , player=user_id)

        if tournament and int(user_id) == int(tournament.player.pk):
            rank = tournament.rank
            return rank
        else:
            return None
    except Tournament.DoesNotExist:
        return None

class TournamentHistoryApiView(APIView):
	def get(self, request, user_id):
		tournaments = OnlinePlayermatch.objects.filter(player=user_id).exclude(game__tournament_id__isnull=True).values_list("game__tournament_id", flat=True).distinct()
		logger.info(f'OnlinePlayerMatch: {tournaments}')
		tournaments = sorted(tournaments, reverse=True)
		tournament_details = []
		gameList = []
		for tid in tournaments:
			game = OnlinePlayermatch.objects.filter(player=user_id, game__tournament_id = tid).order_by('-game__endtime').first()
			if game:
				gameList.append(game)
		logger.info(f'this is list: {gameList}')
		for gameaz in gameList:
			tid = gameaz.game.tournament.pk
			time_passed = calculate_time_passed(gameaz.game.endtime)
			rank = get_rank(user_id, tid)
			tournament_details.append({
					"tournament_id": tid,
					"tournament_time_passed": time_passed,
					"rank": rank if rank is not None else "Rank not found."
				})
			logger.info(f'this is the found game: {time_passed} {rank}')
		return Response({"data": tournament_details}, status=status.HTTP_200_OK)

def get_player_image(self, target_uid, owner_uid, token):
		headers = {
			'X-UID': str(owner_uid),
			'X-TOKEN': token
		}
		logger.info(target_uid)
		opponent_info = requests.get(f'http://userapp:8001/api/user/{target_uid}', headers=headers)
		logger.info("Fetching image")
		return opponent_info.json().get('image')

class TournamentMatchesApiView(APIView):
	def get(self, request, t_id):
		games =	OnlineGame.objects.filter(tournament=t_id)
		owner_uid = request.META.get('HTTP_X_UID')
		owner_token = request.META.get('HTTP_X_TOKEN')
		if not games:
			return Response({"message": "No games found for the given tournament."}, status=status.HTTP_404_NOT_FOUND)
		
		serializer = GameSerializer(games, many=True)

		game_details = []
		for game in games:
			player_arr = OnlinePlayermatch.objects.filter(game=game)
			ser1 = UserSerializer(player_arr[0].player)
			ser2 = UserSerializer(player_arr[1].player)
			player1_image_url = get_player_image(self, player_arr[0].player.uid, owner_uid, owner_token)
			player2_image_url = get_player_image(self, player_arr[1].player.uid, owner_uid, owner_token)
			game_details.append({
				"game_id": game.id,
				"player1": ser1.data.get('uid'),
				"player2": ser2.data.get('uid'),
				"score1": player_arr[0].score,
				"score2": player_arr[1].score,
				"player1_image_url": player1_image_url,
				"player2_image_url": player2_image_url
			})

		return Response({"data":game_details}, status=status.HTTP_200_OK)

def health_check(request):
	return JsonResponse({'status': 'ok'})
