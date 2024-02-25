from django.http import Http404, JsonResponse, HttpResponse
from django.utils.timezone import now
from django.utils import timezone

import requests

from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework import status
import logging

from tour_game.models import Tournament, OnlineGame, OnlinePlayermatch
from tour_api.serializer import TournamentSerializer, GameSerializer
from django.http import HttpResponseBadRequest

logger = logging.getLogger(__name__)

#//Requirement: Get first game ID for tournament (mostly use gameAPI)
#implemented tournamenthistory -> from user ID get all tournaments user participated in and return rank and long ago
#-> call game API for user ID and get the different tournament ids
#-> use long ago function for these tournament game
#-> create rank function and return user rank

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

def update_ranks(request, tournament_id, user_id):
	try:
		tournament = Tournament.objects.get(id=tournament_id)
		for i in range(len(tournament.ranks)):
			if tournament.ranks[i] is None:
				tournament.ranks[i] = user_id
				tournament.save()
				return JsonResponse({'message': 'User added to ranks successfully.'})
		return HttpResponseBadRequest('All ranks are already filled.')

	except Tournament.DoesNotExist:
		return HttpResponseBadRequest('Tournament not found.')

def get_rank(self, user_id, tournament_id):
    try:
        tournament = Tournament.objects.get(id=tournament_id)

        if user_id in tournament.ranks:
            rank_index = tournament.ranks.index(user_id) + 1
            return JsonResponse({'rank': rank_index})
        else:
            return JsonResponse({'message': 'User ID not found in ranks.'})

    except Tournament.DoesNotExist:
        return HttpResponseBadRequest('Tournament not found.')

class TournamentHistoryApiView(APIView):
	def get(self, request, user_id):
		games = OnlineGame.objects.filter(player=user_id)
		tournament_details = []
		for game in games:
			tid = Tournament.objects.get(id=game.tournament)
			time_passed = calculate_time_passed(self, tid.endtime)
			rank = get_rank(self, user_id, tid.id)
			tournament_details.append({
				"tournament_id": tid.id,
				"tournament_time_passed": time_passed,
				"rank": rank
			})
		
		return Response(tournament_details.json(), status=status.HTTP_200_OK)

#Game API get all api matches for specific tournament
#implement tournamentmatches -> all matches for a tid tournament and the scores
#potentially call other api for all game ids

def get_player_image(self, target_uid, owner_uid, token):
		headers = {
			'X-UID': str(owner_uid),
			'X-TOKEN': token
		}
		opponent_info = requests.get(f'http://userapp:3000/users/api/{target_uid}', headers=headers)
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

		game_details - []
		for game in games:
			players = OnlinePlayermatch.objects.filter(game=game)
			player1_image_url = get_player_image(self, OnlinePlayermatch.player[0], owner_uid, owner_token)
			player2_image_url = get_player_image(self, OnlinePlayermatch.player[1], owner_uid, owner_token)
			game_details = []
			game_details.append({
				"game_id": game.id,
				"player1": players[0].player,
				"player2": players[1].player,
				"score1": players[0].score,
				"score2": players[1].score,
				"player1_image_url": player1_image_url,
				"player2_image_url": player2_image_url
			})

		return Response(game_details.json(), status=status.HTTP_200_OK)

def health_check(request):
	return JsonResponse({'status': 'ok'})
