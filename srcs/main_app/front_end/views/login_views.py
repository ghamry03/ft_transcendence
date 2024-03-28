import os
import logging
import requests
from time import time

from main_app.utils import getSessionKey, setSessionKey
from main_app.constants import AUTH_URL, USER_API_URL, REDIRECT_URI

from django.http import JsonResponse
from django.shortcuts import render, redirect
from django.db import connections
from django.db.utils import OperationalError

logger = logging.getLogger(__name__)

# Create your views here.
def loginPage(request):
    context = {
        'authUrl': AUTH_URL,
        'error_message': 'Error encountred'
    }
    return render(request, 'login.html', context)

def authenticate(request):
    files = {
        'grant_type': (None, 'authorization_code'),
        'client_id': (None, os.environ['INTRA_UID']),
        'client_secret': (None, os.environ['INTRA_SECRET']),
        'code': (None, request.GET.get('code')),
        'redirect_uri': (None, REDIRECT_URI),
    }

    context = { 'logged_in': False }
    try:
        response = requests.post('https://api.intra.42.fr/oauth/token', files=files)
    except requests.RequestException as e:
        return render(request, 'base.html', context=context, status=500)

    if response.status_code == 200:
        json_response = response.json()
        access_token = json_response.get('access_token', None)
        refresh_token = json_response.get('refresh_token', None)
        setSessionKey(request, 'access_token', access_token)
        setSessionKey(request, 'refresh_token', refresh_token)
        setSessionKey(request, 'token_expiry', int(json_response.get('created_at')) + 7200)

        if access_token:
            headers = {
                'Authorization': 'Bearer ' + access_token,
            }

            try:
                me_response = requests.get('https://api.intra.42.fr/v2/me', headers=headers)
                me_response.raise_for_status()
            except requests.RequestException as e:
                return render(request, 'base.html', context=context, status=500)

            UID = str(me_response.json()['id'])
            headers = {
                'X-UID': UID,
                'X-TOKEN': access_token
            }

            try:
                user_api_response = requests.get(USER_API_URL + 'api/user/' + UID, headers=headers)
                user_api_response.raise_for_status()
                setSessionKey(request, 'userData', user_api_response.json())
                setSessionKey(request, 'logged_in', True)
            except requests.RequestException as e:
                return render(request, 'base.html', context=context, status=500)
            return redirect('/')
    try:
        request.session.flush()
    except:
        pass
    return redirect('/')

def logout(request):
    context = {
        'authUrl': AUTH_URL
    }
    #TODO: display error msg that session didn't get flushed
    try:
        db_conn = connections['default']
        db_conn.cursor()
    except OperationalError:
        logger.debug(f"can't flush the session, redirecting to login page")
    else:
        logger.debug(f"session flushed, redirecting to login page")
    return render(request, 'login.html', context)

def renew_token(request):
    # status=e.request.status_code if e.response else 500
    token_expiry = getSessionKey(request, 'token_expiry') or 0
    if token_expiry < int(time()):
        return JsonResponse({'error': 'Token already expired'}, status=400)

    refresh_token = getSessionKey(request, 'refresh_token')
    files = {
        'grant_type': 'refresh_token',
        'refresh_token': refresh_token,
        'client_id': (None, os.environ['INTRA_UID']),
        'client_secret': (None, os.environ['INTRA_SECRET'])
    }

    try:
        response = requests.post('https://api.intra.42.fr/oauth/token', files=files)
    except requests.RequestException as e:
        return JsonResponse({'error': 'Failed to update status', 'details': str(e)}, status=500)


    if response.status_code == 200:
        json_response = response.json()
        setSessionKey(request, 'access_token', json_response.get('access_token', None))
        setSessionKey(request, 'refresh_token', json_response.get('refresh_token', None))
        setSessionKey(request, 'token_expiry', int(json_response.get('created_at')) + 7200)
        return JsonResponse({'message': 'Token renewed successfully'}, status=200)
    else:
        error_message = response.json().get('error', 'intra issue')
        return JsonResponse({'error': error_message}, status=response.status_code)
