from asgiref.sync import sync_to_async
from django.utils import timezone
from .models import UserApiUser, Game, PlayerMatch

@sync_to_async
def createGame(pid1, pid2):
	game = Game.objects.create(
		starttime=timezone.now()
	)
	player1 = UserApiUser.objects.get(uid=int(pid1))
	PlayerMatch.objects.create(
		game=game,
		player=player1,
		score=0
	)
	player2 = UserApiUser.objects.get(uid=int(pid2))
	PlayerMatch.objects.create(
		game=game,
		player=player2,
		score=0
	)
	return game.id

@sync_to_async
def endGame(gid, pid1, pid2, score1, score2):
	game = Game.objects.get(id=int(gid))
	game.endtime = timezone.now()
	game.save()

	player1 = PlayerMatch.objects.get(game=gid, player=pid1)
	player1.score = score1
	player1.save()

	player2 = PlayerMatch.objects.get(game=gid, player=pid2)
	player2.score = score2
	player2.save()
