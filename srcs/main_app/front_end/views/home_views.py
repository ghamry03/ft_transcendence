import requests, logging

from main_app.utils import getSessionKey, make_request
from main_app.constants import TOURNAMENT_HISOTRY_URL, MATCH_HISOTRY_URL, FRIEND_API_URL

from django.http import HttpResponse, JsonResponse
from django.shortcuts import render

logger = logging.getLogger(__name__)

def index(request, status=None):
    context = { 'logged_in': getSessionKey(request, 'logged_in') }
    return render(request, 'base.html', context=context)

def getTournamentHistory(uid):
    response, isError = make_request(TOURNAMENT_HISOTRY_URL + f'api/tourhistory/{uid}')

    if isError:
        return None

    return response.json()['data']

def getMatchHistory(uid):
    response, isError = make_request(MATCH_HISOTRY_URL + f'game/matchhistory/{uid}')

    if isError:
        return None

    return response.json()

def getFriendsList(uid, accessToken):
    headers = { 'Content-Type': 'application/json' }
    response, isError = make_request(
        FRIEND_API_URL + "api/friends/",
        headers=headers,
        json = {
            "uid": f"{uid}",
            "ownerUID": f"{uid}",
            "access_token": accessToken
        },
    )

    if isError:
        return JsonResponse({})

    return response.json()

def homePage(request):
    userData = getSessionKey(request, 'userData')
    uid = userData.get('uid', None) if userData else None
    accessToken = getSessionKey(request, 'access_token')

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
    logged_in = getSessionKey(request, 'logged_in')
    if not logged_in or logged_in == False:
        return render(request, 'topBar.html')

    userData = getSessionKey(request, 'userData')

    return render(request, 'topBar.html', {
        'userData': userData,
    })

def homeCards(request):
    userData = getSessionKey(request, 'userData')
    uid = userData.get('uid', None) if userData else None

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
