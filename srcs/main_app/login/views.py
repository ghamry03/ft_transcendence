import environ
import os
import requests
from django.shortcuts import render, redirect
from django.http import HttpResponse
from . import AUTH_URL, USER_API_URL

# Create your views here.
def loginPage(request):
    context = {
        'authUrl': AUTH_URL
    }
    return render(request, 'login.html', context)

def logout(request):
    context = {
        'authUrl': AUTH_URL
    }
    request.session.flush()
    return render(request, 'login.html', context)


def authenticate(request):
    files = {
        'grant_type': (None, 'authorization_code'),
        'client_id': (None, os.environ['INTRA_UID']),
        'client_secret': (None, os.environ['INTRA_SECRET']),
        'code': (None, request.GET.get('code')),
        'redirect_uri': (None, 'http://127.0.0.1:8000/authenticate/'),
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
            user_api_response = requests.get(USER_API_URL + '/users/api/' + UID, headers=headers)
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
