from asgiref.sync import sync_to_async
from django.utils import timezone
from .models import UserApiUser, Game, PlayerMatch
from django.db import connections
from django.db.utils import OperationalError
import logging

logger = logging.getLogger(__name__)

def checkDbHealth():
	db_conn = connections['default']
	try:
		db_conn.cursor()
	except OperationalError:
		logger.info(f"game: can't connect to db")
		return False
	else:
		logger.info(f'game: db connection is alive')
		return True

@sync_to_async
def createGame(pid1, pid2):
	logger.info("gamedb: creating game")
	if not checkDbHealth():
		return None
	try:
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
	except:
		logger.info("creategame: db failed")
		return None 

@sync_to_async
def endGame(gid, pid1, pid2, score1, score2):
	logger.info("gamedb: ending game")
	if not checkDbHealth():
		return None
	try:
		game = Game.objects.get(id=int(gid))
		game.endtime = timezone.now()
		game.save()

		player1 = PlayerMatch.objects.get(game=gid, player=pid1)
		player1.score = score1
		player1.save()

		player2 = PlayerMatch.objects.get(game=gid, player=pid2)
		player2.score = score2
		player2.save()
		return gid
	except:
		logger.info("endgame: db failed")
		return None 
