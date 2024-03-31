import requests

from main_app.utils import make_request
from main_app.constants import MATCH_HISOTRY_URL, GAME_URL, TOUR_URL

from django.shortcuts import render
from django.http import JsonResponse, HttpResponse

# Create your views here
def onlineGame(request):
    response, isError = make_request(f"{MATCH_HISOTRY_URL}game/health")
    if isError:
        return response

    return render(request, 'game.html')

def offlineGame(request):
    context = {
    }
    return render(request, 'offline.html', context)

def tournament(request):
    response, isError = make_request(f"{MATCH_HISOTRY_URL}game/health")
    if isError:
        return response

    return render(request, 'tournament.html')

def getGameUrl(request):
    return HttpResponse(GAME_URL)

def getTourUrl(request):
    return HttpResponse(TOUR_URL)
