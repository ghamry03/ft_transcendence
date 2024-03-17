from django.http import Http404, JsonResponse, HttpResponse
from django.utils.timezone import now
from django.utils import timezone
from django.db import models

import requests

from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework import status
import logging

from online.models import PlayerMatch, Game, TourGameTournament
from game_api.serializer import MatchSerializer, GameSerializer

logger = logging.getLogger(__name__)

# List view of all Matches for a given User and his scores
class UserMatchListApiView(APIView):
	def get(self, request, player_id):
		matches = PlayerMatch.objects.filter(player=player_id)
		if not matches:
			return Response({"message": "No matches found for the given player."}, status=status.HTTP_404_NOT_FOUND)
		serializer = MatchSerializer(matches, many=True)
		return Response(serializer.data, status=status.HTTP_200_OK)

# List view of all Games for a given Tournament
class TournamentGameListApiView(APIView):
	def get(self, request, tournament_id):
		games = Game.objects.filter(id=tournament_id)
		if not games:
			return Response({"message": "No games found for the given tournament."}, status=status.HTTP_404_NOT_FOUND)
		serializer = GameSerializer(games, many=True)
		return Response(serializer.data, status=status.HTTP_200_OK)

# List all players in a given match
class MatchPlayerListApiView(APIView):
	def get(self, request, match_id):
		players = PlayerMatch.objects.filter(game=match_id)
		if not players:
			return Response({"message": "No players found for the given match."}, status=status.HTTP_404_NOT_FOUND)
		serializer = MatchSerializer(players, many=True)
		return Response(serializer.data, status=status.HTTP_200_OK)

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

def get_player_image(self, target_uid, owner_uid, token):
		headers = {
			'X-UID': str(owner_uid),
			'X-TOKEN': token
		}
		opponent_info = requests.get(f'http://userapp:8001/users/api/{target_uid}', headers=headers)
		logger.info("Fetching opponent image")
		return opponent_info.json().get('image')

class   MatchHistoryApiView(APIView):
	def get(self, request, user_id):
		# Retrieve all matches for the user
		user_matches = PlayerMatch.objects.filter(player = user_id)
		if not user_matches: # TODO: Return empty response
			return Response({"message": "No matches found for the given user."}, status=status.HTTP_404_NOT_FOUND)

		games_details = []
		for match in user_matches:
			token = request.META.get('HTTP_X_TOKEN')

			# Fetching the game this match is part of
			game = match.game

			# Calculate time passed since the game ended
			time_passed = calculate_time_passed(self, game.endtime)

			# Fetching all player matches for this game, including the user and opponents
			all_player_matches = PlayerMatch.objects.filter(game=game)

			# Extracting user's score and opponents' details
			opponents_details = []
			for player_match in all_player_matches:
				if player_match.player.uid != user_id:
					opponent_image_url = get_player_image(self, 
					player_match.player.uid, user_id, token)
					opponents_details.append({
						"opponent_id": player_match.player.uid,
						"opponent_score": player_match.score,
						"opponent_image_url": opponent_image_url
					})
				else:
					my_score = player_match.score

			game_data = {
				"game_id": game.id,
				"my_score": my_score,
				"opponents": opponents_details,
				"timePassed": time_passed
			}
			games_details.append(game_data)

		return Response(games_details, status=status.HTTP_200_OK)

class CreateGameApiView(APIView):
	def get(self, request, pid1, pid2, tid):
		logger.info("creating a db record")
		tour = TourGameTournament.objects.get(id=tid)
		game = Game.objects.create(
			starttime=timezone.now(),
			tournament=tour
		)
		player1 = User.objects.get(uid=pid1, on_delete=models.CASCADE)
		PlayerMatch.objects.create(
			game=game,
			player=player1,
			score=0
		)
		player2 = User.objects.get(uid=pid2, on_delete=models.CASCADE)
		PlayerMatch.objects.create(
			game=game,
			player=player2,
			score=0
		)
		return HttpResponse(game.id)

class EndGameApiView(APIView):
	def get(self, request, gid, pid1, pid2, score1, score2):
		game = Game.objects.get(id=int(gid))
		game.endtime = timezone.now()
		game.save()

		player1 = PlayerMatch.objects.get(game=gid, player=pid1)
		player1.score = score1
		player1.save()

		player2 = PlayerMatch.objects.get(game=gid, player=pid2)
		player2.score = score2
		player2.save()
		return Response(status=status.HTTP_200_OK)

def health_check(request):
	return JsonResponse({'status': 'ok'})
