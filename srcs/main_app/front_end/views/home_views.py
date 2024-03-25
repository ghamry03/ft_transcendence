import requests, logging

from main_app.constants import TOURNAMENT_HISOTRY_URL, MATCH_HISOTRY_URL

from django.http import HttpResponse, JsonResponse
from django.shortcuts import render

logger = logging.getLogger(__name__)

def index(request):
    return render(request, 'base.html')

def getTournamentHistory(uid):
    try:
        response = requests.get(TOURNAMENT_HISOTRY_URL + f'api/tourhistory/{uid}')
    except:
        return None

    if response.status_code == 200:
        return response.json()['data']
    return None

def getMatchHistory(uid):
    try:
        response = requests.get(MATCH_HISOTRY_URL + f'game/matchhistory/{uid}')
    except:
        return None

    if response.status_code == 200:
        return response.json()
    return None

def getFriendsList(uid, accessToken):
    headers = { 'Content-Type': 'application/json' }
    try:
        response = requests.get(
            'http://friendsapp:8002/' + "api/friends/",
            headers=headers,
            json={
                "uid": f"{uid}",
                "ownerUID": f"{uid}",
                "access_token": accessToken
                },
        )
    except requests.RequestException as e:
        return JsonResponse({})

    if response.status_code == 200:
        return response.json()
    return JsonResponse({})

def homePage(request):
    userData = request.session.get('userData', None)
    uid = userData.get('uid', None)
    accessToken = request.session.get('access_token', None)

    friendsList = getFriendsList(uid, accessToken)

    context = {
        "userData": userData,
        "friendsList": friendsList['friendsList'],
        "friendRequests": friendsList['friendRequests'],
        }

    httpResponse = HttpResponse(render(request, 'home.html', context))
    httpResponse.set_cookie('uid' , uid)

    return httpResponse

def topBar(request):
    logged_in = request.session.get('logged_in', None)
    if 'logged_in' not in request.session or logged_in == False:
        return render(request, 'topBar.html')

    userData = request.session.get('userData', None)

    return render(request, 'topBar.html', {
        'userData': userData,
    })

def homeCards(request):
    userData = request.session.get('userData', None)
    uid = userData.get('uid', None)
    tournamentHistory = getTournamentHistory(uid)
    matchHistory = getMatchHistory(uid)

    logger.debug(f'This is the users match history: {matchHistory}');
    logger.debug(f'This is the users tournament history: {tournamentHistory}');
    context = {
        'userData': userData,
        "tournamentHistory": tournamentHistory,
        "matchHistory": matchHistory,
    }
    return render(request, 'homeCards.html', context)
