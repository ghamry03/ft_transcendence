from django.http import Http404, JsonResponse, HttpResponse
from django.utils.timezone import now
from django.utils import timezone

import requests

from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework import status
import logging

from tour_game.models import Tournament, OnlineGame, OnlinePlayermatch, TournamentRank
from tour_api.serializer import TournamentSerializer, GameSerializer, UserSerializer
from django.http import HttpResponseBadRequest

logger = logging.getLogger(__name__)

def calculate_time_passed(self, game_endtime):
		current_time = now()
		time_difference = current_time - game_endtime

		if time_difference.days >= 1:
			if time_difference.days == 1:
				return "1 day"
			return f"{time_difference.days} days"
		elif time_difference.seconds >= 3600:
			hours_passed = time_difference.seconds // 3600
			if hours_passed == 1:
				return "1 hour"
			return f"{hours_passed} hours"
		elif time_difference.seconds >= 60:
			minutes_passed = time_difference.seconds // 60
			if minutes_passed == 1:
				return "1 minute"
			return f"{minutes_passed} minutes"
		else:
			if time_difference.seconds == 1:
				return "1 second"
			return f"{time_difference.seconds} seconds"

# class UpdateRank(APIView):
# 	# allowed_methods = ['POST', 'OPTIONS'] 
# 	def get(self, request, tid, uid, rank):
# 		logger.info("Updating rank")
# 		try:
# 			tour = Tournament.objects.get(id=tid)
# 			tourRank = TournamentRank.objects.create(
# 				playerID=uid,
# 				rank=rank,
# 				tournament=tour
# 			)
# 			tourRank.save()
# 			return JsonResponse({'message': 'User added to ranks successfully.'})
		
# 		except Tournament.DoesNotExist:
# 			return HttpResponseBadRequest('Tournament not found.')

def get_rank(user_id, tournament_id):
    try:
        tournament = TournamentRank.objects.get(tournament=tournament_id)

        if int(user_id) == int(tournament.playerID):
            rank = tournament.rank
            return rank
        else:
            return None

    except Tournament.DoesNotExist:
        return None

class TournamentHistoryApiView(APIView):
	def get(self, request, user_id):
		#Exclude was adding because it was crashing when the queryset included a match that didnt belong to a tournament needs testing
		games = OnlinePlayermatch.objects.filter(player=user_id).exclude(game__tournament_id__isnull=True)
		logger.info(f'OnlinePlayerMatch: {games}')
		tournament_details = []
		for game in games:
			logger.info(f'this is the tour game: {game.game.tournament}')
			tid = game.game.tournament.id
			time_passed = calculate_time_passed(self, game.game.endtime)
			rank = get_rank(user_id, tid)
			if rank is not None:
				tournament_details.append({
					"tournament_id": tid,
					"tournament_time_passed": time_passed,
					"rank": rank
				})
			else:
				tournament_details.append({
					"tournament_id": tid,
					"tournament_time_passed": time_passed,
					"rank": "Rank not found."
				})
		return Response({"data":tournament_details}, status=status.HTTP_200_OK)

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
