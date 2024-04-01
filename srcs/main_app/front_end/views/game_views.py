import logging

from main_app.utils import make_request
from main_app.constants import MATCH_HISOTRY_URL, TOURNAMENT_HISOTRY_URL, GAME_URL, TOUR_URL

from django.shortcuts import render
from django.http import JsonResponse, HttpResponse

logger = logging.getLogger(__name__)

# Create your views here
def onlineGame(request):
    return render(request, 'game.html')

def offlineGame(request):
    context = {
    }
    return render(request, 'offline.html', context)

def tournament(request):
    return render(request, 'tournament.html')

def getGameUrl(request):
    return HttpResponse(GAME_URL)

def getTourUrl(request):
    return HttpResponse(TOUR_URL)
