from django.conf import settings
from django.shortcuts import render
from django.http import HttpResponse, JsonResponse, HttpResponseBadRequest, HttpResponseNotFound
from django.views.generic import View
import requests, logging
from django.utils.decorators import method_decorator
from .hostnameAuthentication import hostname_whitelist
from django.conf import settings
from django.contrib.sessions.models import Session


logger = logging.getLogger(__name__)

from . import FRIEND_API_URL, TOURNAMENT_HISOTRY_URL, USER_API_URL

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
        json={
            "uid": f"{uid}",
            "ownerUID": f"{uid}",
            "access_token": request.session['access_token']
            },
    ).json()

    tournamentHistory = requests.get(
        TOURNAMENT_HISOTRY_URL + "api/tourhistory/" + f'{uid}'
    ).json()

    context = {"userData": request.session["userData"], "friendsList": friendsList['friendsList'] }

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

def searchUsers(request, username):
    headers = {
        'X-UID': f'{request.session['userData']['uid']}',
        'X-TOKEN': request.session['access_token']
    }

    base_url = USER_API_URL + 'users/api/'
    
    response = requests.get(base_url, headers=headers)
    
    if response.status_code == 200:
        data = {
            'status': response.status_code,
            'data': response.json(),
            'uid': request.session['userData']['uid']
            }
        logger.debug(data)
        return render(request, 'searchedUser.html', data)
    else:
        logger.debug(f"Error: {response.status_code}")
        return HttpResponse()
    
def addUser(request, friendUID):
    headers = { 'Content-Type': 'application/json' }

    myuid = request.session['userData']['uid']

    response = requests.post(
        FRIEND_API_URL + "api/friends/",
        headers=headers,
        json={
            "first_id": f'{myuid}',
            "second_id": f'{friendUID}', 
            "session_id": request.session.session_key, 
            "access_token": request.session['access_token'], 
            },
    ).json()

    return HttpResponse()

def acceptFriend(request, friendUID):
    headers = { 'Content-Type': 'application/json' }

    myuid = request.session['userData']['uid']

    response = requests.put(
        FRIEND_API_URL + "api/friends/",
        headers=headers,
        json={
            "first_user": f'{myuid}',
            "second_user": f'{friendUID}', 
            "relationship": 0, 
            "session_id": request.session.session_key, 
            "access_token": request.session['access_token'],
            },
    ).json()
    return HttpResponse()


def rejectFriend(request, friendUID):
    headers = { 'Content-Type': 'application/json' }

    myuid = request.session['userData']['uid']

    response = requests.delete(
        FRIEND_API_URL + "api/friends/",
        headers=headers,
        json={
            "first_user": f'{myuid}',
            "second_user": f'{friendUID}', 
            "session_id": request.session.session_key, 
            "access_token": request.session['access_token'],
            },
    ).json()
    return HttpResponse()


@method_decorator(hostname_whitelist(settings.ALLOWED_HOSTNAMES_FOR_API), name='dispatch')
class SessionDataView(View):
    def get(self, request, *args, **kwargs):
        session_id = request.GET.get('sessionID')
        if not session_id:
            return HttpResponseBadRequest('The sessionID parameter is required.')
        
        try:
            session = Session.objects.get(session_key=session_id)
            session_data = session.get_decoded()
        except Session.DoesNotExist:
            return HttpResponseNotFound('Session data not found.')
        
        return JsonResponse({'sessionData': session_data})