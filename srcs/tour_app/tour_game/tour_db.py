from asgiref.sync import sync_to_async
from django.utils import timezone
from .models import UserApiUser, Tournament, TournamentRank
from django.db import connections
from django.db.utils import OperationalError
import logging

logger = logging.getLogger(__name__)

def checkDbHealth():
	db_conn = connections['default']
	try:
		db_conn.cursor()
	except OperationalError:
		logger.info(f"tour: can't connect to db")
		return False
	else:
		logger.info(f'tour: db connection is alive')
		return True

@sync_to_async
def createTournament():
	logger.info("tourdb: creating tour")
	if not checkDbHealth():
		return None
	try:
		tour = Tournament.objects.create(
			starttime=timezone.now()
		)
		return tour.id
	except:
		logger.info("createtour: db failed")
		return None

@sync_to_async
def deleteTournament(tid):
	logger.info("tourdb: deleting tour")
	if not checkDbHealth():
		return None
	try:
		Tournament.objects.get(id=tid).delete()
		return tid
	except:
		logger.info("deletetour: db failed")
		return None 

@sync_to_async
def endTournament(tid):
	logger.info("tourdb: ending tour")
	if not checkDbHealth():
		return None
	try:
		tour = Tournament.objects.get(id=tid)
		tour.endtime = timezone.now()
		tour.save()
		return tid
	except:
		logger.info("endtour: db failed")
		return None 


@sync_to_async
def updateRank(tid, uid, rank):
	logger.info("tourdb: updating rank for %d %d %d", tid, uid, rank)
	if not checkDbHealth():
		return None
	try:
		tour = Tournament.objects.get(id=tid)
		player = UserApiUser.objects.get(uid=uid)
		try:
			tourRank = TournamentRank.objects.get(tournament=tour, player=player)
			tourRank.rank = rank
			tourRank.save()
			return tid
		except:
			tourRank = TournamentRank.objects.create(
				player=player,
				rank=rank,
				tournament=tour
			)
			tourRank.save()
			return tid
	except:
		logger.info("updaterank: db failed")
		return None 
