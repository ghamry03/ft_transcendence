import os
import logging
from time import time

from main_app.utils import getSessionKey, setSessionKey, make_request
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
    response, isError = make_request(request, 'https://api.intra.42.fr/oauth/token', method='post', files=files)
    if isError:
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

            me_response, isError = make_request(request, 'https://api.intra.42.fr/v2/me', headers=headers)
            if isError:
                redirect('/')
                # return render(request, 'base.html', context=context, status=500)

            UID = str(me_response.json()['id'])
            headers = {
                'X-UID': UID,
                'X-TOKEN': access_token
            }

            user_api_response, isError = make_request(request, USER_API_URL + 'api/user/' + UID, headers=headers)
            if isError:
                redirect('/')
            user_api_response.raise_for_status()
            setSessionKey(request, 'userData', user_api_response.json())
            setSessionKey(request, 'logged_in', True)
                # return render(request, 'base.html', context=context, status=500)
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
        request.session.flush()
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

    response, isError = make_request(request, 'https://api.intra.42.fr/oauth/token', files=files)
    if isError:
        return JsonResponse({'error': 'Failed to update status'}, status=500)


    if response.status_code == 200:
        json_response = response.json()
        setSessionKey(request, 'access_token', json_response.get('access_token', None))
        setSessionKey(request, 'refresh_token', json_response.get('refresh_token', None))
        setSessionKey(request, 'token_expiry', int(json_response.get('created_at')) + 7200)
        return JsonResponse({'message': 'Token renewed successfully'}, status=200)
    else:
        error_message = response.json().get('error', 'intra issue')
        return JsonResponse({'error': error_message}, status=response.status_code)
