from asgiref.sync import sync_to_async
from django.utils import timezone
from .models import UserApiUser, OnlineGame, OnlinePlayermatch, Tournament

@sync_to_async
def createTournament():
	tour = Tournament.objects.create(
		starttime=timezone.now()
	)
	return tour.id

@sync_to_async
def createGame(pid1, pid2, tour):
	game = OnlineGame.objects.create(
		starttime=timezone.now(),
		tournament=tour
	)
	player1 = UserApiUser.objects.get(uid=pid1)
	OnlinePlayermatch.objects.create(
		game=game,
		player=player1,
		score=0
	)
	player2 = UserApiUser.objects.get(uid=pid2)
	OnlinePlayermatch.objects.create(
		game=game,
		player=player2,
		score=0
	)
	return game.id