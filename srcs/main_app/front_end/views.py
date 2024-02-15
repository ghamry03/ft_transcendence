from django.shortcuts import render,redirect
from django.http import HttpResponse, JsonResponse
import requests
import environ
import os

# Create your views here.
def index(request):
    return render(request, 'base.html')

def loginPage(request):
    context = {
        'authUrl': environ.Env()('AUTH_URL')
    }
    return render(request, 'login.html', context)

def logout(request):
    context = {
        'authUrl': environ.Env()('AUTH_URL')
    }
    request.session.flush()
    return render(request, 'login.html', context)


def topBar(request):
    if 'logged_in' not in request.session or request.session['logged_in'] == False:
        return render(request, 'topBar.html')

    return render(request, 'topBar.html', {
        'userData': request.session['userData']
    })

def token(request):
    files = {
        'grant_type': (None, 'authorization_code'),
        'client_id': (None, os.environ['INTRA_UID']),
        'client_secret': (None, os.environ['INTRA_SECRET']),
        'code': (None, request.GET.get('code')),
        'redirect_uri': (None, 'http://127.0.0.1:8000/token'),
    }
    response = requests.post('https://api.intra.42.fr/oauth/token', files=files)
    if response.status_code == 200:
        json_response = response.json()
        access_token = json_response.get('access_token', None)
        refresh_token = json_response.get('refresh_token', None)
        request.session['access_token'] = access_token
        request.session['refresh_token'] = refresh_token

        if access_token:
            headers = {
                'Authorization': 'Bearer ' + access_token,
            }

            me_response = requests.get('https://api.intra.42.fr/v2/me', headers=headers)
            UID = str(me_response.json()['id'])
            headers = {
                'X-UID': UID,
                'X-TOKEN': access_token
            }
            user_api_response = requests.get(environ.Env()('USER_API_URL') + '/users/api/' + UID, headers=headers)
            request.session['userData'] = user_api_response.json()
            request.session['logged_in'] = True
            return redirect('/')
    try:
        request.session.flush()
    except KeyError:
        pass
    return redirect('/')


def renew_token(request):
    files = {
        'grant_type': (None, 'refresh_token'),
        'refresh_token': (None, request.session['refresh_token']),
        'client_id': (None, os.environ['INTRA_UID']),
        'client_secret': (None, os.environ['INTRA_SECRET'])
    }
    response = requests.post('https://api.intra.42.fr/oauth/token', files=files)
    if response.status_code == 200:
        json_response = response.json()
        request.session['access_token'] = json_response.get('access_token', None)
        request.session['refresh_token'] = json_response.get('refresh_token', None)
    else:
        request.session.flush()
    return HttpResponse(status=response.status_code)


def homePage(request):
    context = {
        'userData' : request.session['userData'],
    }

    httpResponse = HttpResponse(render(request, 'home.html', context))
    httpResponse.set_cookie('uid' , request.session['userData']['uid'])
    httpResponse.set_cookie('token' , request.session['access_token'])
    return httpResponse
    # return render(request, 'home.html', {
    #     'userData': request.session['userData'],
    # })

def homeCards(request):
    context = {
        'userData': request.session['userData'],
    }
    return render(request, 'homeCards.html', context)


def onlineGame(request):
    context = {
    }
    return render(request, 'game.html', context)

def offlineGame(request):
    context = {
    }
    return render(request, 'offline.html', context)

def getOpponentInfo(request):
    ownerUid = request.GET.get('ownerUid')
    targetUid = request.GET.get('targetUid')
    token = request.GET.get('token')
    headers = {
        'X-UID': ownerUid,
        'X-TOKEN': token
    }
    opponentInfo = requests.get('http://userapp:3000/users/api/' + targetUid, headers=headers)
    return JsonResponse(opponentInfo.json())
