from django.shortcuts import render

# Create your views here
def onlineGame(request):
    context = {
    }
    return render(request, 'game.html', context)

def offlineGame(request):
    context = {
    }
    return render(request, 'offline.html', context)

