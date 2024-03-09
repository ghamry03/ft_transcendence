from django.shortcuts import render
from django.http import HttpResponse, JsonResponse
import requests, logging

logger = logging.getLogger(__name__)

from . import FRIEND_API_URL, TOURNAMENT_HISOTRY_URL

# Create your views here.
def index(request):
    return render(request, 'base.html')

def topBar(request):
    if 'logged_in' not in request.session or request.session['logged_in'] == False:
        return render(request, 'topBar.html')

    return render(request, 'topBar.html', {
        'userData': request.session['userData']
    })

def homePage(request):
    headers = { 'Content-Type': 'application/json' }

    uid = request.session['userData']['uid']

    friendsList = requests.get(
        FRIEND_API_URL + "api/friends/",
        headers=headers,
        json={"id": f"{uid}", "type": 1},
    ).json()

    # Swap the first and second user if we're the first user as
    # the home.html depends on the first user being the friend
    friendsList = map(
        lambda f: (f["first_id"] if f["second_id"]["uid"] == uid else f["second_id"]),
        friendsList,
    )

    tournamentHistory = requests.get(
        TOURNAMENT_HISOTRY_URL + "api/tourhistory/" + f'{uid}'
    ).json()

    context = {"userData": request.session["userData"], "friendsList": list(friendsList)}

    httpResponse = HttpResponse(render(request, 'home.html', context))
    httpResponse.set_cookie('uid' , uid)

    return httpResponse

def homeCards(request):
    context = {
        'userData': request.session['userData'],
    }
    return render(request, 'homeCards.html', context)

def getOpponentInfo(request):
    ownerUid = request.GET.get('ownerUid')
    targetUid = request.GET.get('targetUid')
    token = request.session['access_token']
    # token = request.GET.get('token')
    headers = {
        'X-UID': ownerUid,
        'X-TOKEN': token
    }
    opponentInfo = requests.get('http://userapp:3000/users/api/' + targetUid, headers=headers)
    return JsonResponse(opponentInfo.json())
