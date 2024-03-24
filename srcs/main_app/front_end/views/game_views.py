from django.shortcuts import render
from django.http import JsonResponse

# Create your views here
def onlineGame(request):
    context = {
    }
    # return JsonResponse(data={}, status=500)
    return render(request, 'game.html', context)

def offlineGame(request):
    context = {
    }
    return render(request, 'offline.html', context)

def tournament(request):
    context = {
    }
    return render(request, 'tournament.html', context)
