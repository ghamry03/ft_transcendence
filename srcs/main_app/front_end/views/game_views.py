import requests
from main_app.constants import MATCH_HISOTRY_URL, TOURNAMENT_HISOTRY_URL, GAME_URL, TOUR_URL

from django.shortcuts import render
from django.http import JsonResponse, HttpResponse

# Create your views here
def onlineGame(request):
    try:
        response = requests.get(f"{MATCH_HISOTRY_URL}game/health")
        response.raise_for_status()
    except requests.RequestException as e:
        return JsonResponse({'error': 'Failed to update profile', 'details': str(e)}, status=500)

    return render(request, 'game.html')

def offlineGame(request):
    context = {
    }
    return render(request, 'offline.html', context)

def tournament(request):
    try:
        response = requests.get(f"{TOURNAMENT_HISOTRY_URL}api/health")
        response.raise_for_status()
    except requests.RequestException as e:
        return JsonResponse({'error': 'Failed to update profile', 'details': str(e)}, status=500)

    return render(request, 'tournament.html')

def getGameUrl(request):
    return HttpResponse(GAME_URL)

def getTourUrl(request):
    return HttpResponse(TOUR_URL)
