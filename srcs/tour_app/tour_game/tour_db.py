from asgiref.sync import sync_to_async
from django.utils import timezone
from .models import UserApiUser, OnlineGame, OnlinePlayermatch, Tournament

@sync_to_async
def createTournament():
	tour = Tournament.objects.create(
		starttime=timezone.now()
	)
	return tour.id

# @sync_to_async
# def createGame(pid1, pid2, tour):
# 	game = OnlineGame.objects.create(
# 		starttime=timezone.now(),
# 		tournament=tour
# 	)
# 	player1 = UserApiUser.objects.get(uid=pid1)
# 	OnlinePlayermatch.objects.create(
# 		game=game,
# 		player=player1,
# 		score=0
# 	)
# 	player2 = UserApiUser.objects.get(uid=pid2)
# 	OnlinePlayermatch.objects.create(
# 		game=game,
# 		player=player2,
# 		score=0
# 	)
# 	return game.id

# @sync_to_async
# def endGame(gid, pid1, pid2, score1, score2):
# 	game = OnlineGame.objects.get(id=int(gid))
# 	game.endtime = timezone.now()
# 	game.save()

# 	player1 = OnlinePlayermatch.objects.get(game=gid, player=pid1)
# 	player1.score = score1
# 	player1.save()

# 	player2 = OnlinePlayermatch.objects.get(game=gid, player=pid2)
# 	player2.score = score2
# 	player2.save()
