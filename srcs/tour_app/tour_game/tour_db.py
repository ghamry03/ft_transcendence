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
def deleteTournament(tid):
	Tournament.objects.get(id=tid).delete()

@sync_to_async
def endTournament(tid):
	tour = Tournament.objects.get(id=tid)
	tour.endtime = timezone.now()
	tour.save()
