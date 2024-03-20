import requests

from main_app.constants import TOURNAMENT_HISOTRY_URL

from django.http import HttpResponse
from django.shortcuts import render


def index(request):
    return render(request, 'base.html')

def homePage(request):
    headers = { 'Content-Type': 'application/json' }

    uid = request.session['userData']['uid']

    friendsList = requests.get(
        'http://friendsapp:8002/' + "api/friends/",
        headers=headers,
        json={
            "uid": f"{uid}",
            "ownerUID": f"{uid}",
            "access_token": request.session['access_token']
            },
    ).json()

    tournamentHistory = requests.get(
        TOURNAMENT_HISOTRY_URL + "api/tourhistory/" + f'{uid}'
    ).json()

    context = {"userData": request.session["userData"], "friendsList": friendsList['friendsList'], "friendRequests": friendsList['friendRequests']}

    httpResponse = HttpResponse(render(request, 'home.html', context))
    httpResponse.set_cookie('uid' , uid)

    return httpResponse

def topBar(request):
    if 'logged_in' not in request.session or request.session['logged_in'] == False:
        return render(request, 'topBar.html')

    return render(request, 'topBar.html', {
        'userData': request.session['userData'],
    })

def homeCards(request):
    context = {
        'userData': request.session['userData'],
    }
    return render(request, 'homeCards.html', context)
