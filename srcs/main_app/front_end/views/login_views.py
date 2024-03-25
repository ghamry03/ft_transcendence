import os
import requests
from time import time

from main_app.constants import AUTH_URL, USER_API_URL, REDIRECT_URI

from django.http import JsonResponse
from django.shortcuts import render, redirect


# Create your views here.
def loginPage(request):
    context = {
        'authUrl': AUTH_URL
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
    try:
        response = requests.post('https://api.intra.42.fr/oauth/token', files=files)
    except requests.RequestException as e:
        return JsonResponse({'error': 'Failed to update status', 'details': str(e)}, status=500)

    if response.status_code == 200:
        json_response = response.json()
        access_token = json_response.get('access_token', None)
        refresh_token = json_response.get('refresh_token', None)
        request.session['access_token'] = access_token
        request.session['refresh_token'] = refresh_token
        request.session['token_expiry'] = int(json_response.get('created_at')) + 7200

        if access_token:
            headers = {
                'Authorization': 'Bearer ' + access_token,
            }

            try:
                me_response = requests.get('https://api.intra.42.fr/v2/me', headers=headers)
                me_response.raise_for_status()
            except requests.RequestException as e:
                return JsonResponse({'error': 'Failed to update status', 'details': str(e)}, status=500)

            UID = str(me_response.json()['id'])
            headers = {
                'X-UID': UID,
                'X-TOKEN': access_token
            }

            user_api_response = requests.get(USER_API_URL + 'api/user/' + UID, headers=headers)
            request.session['userData'] = user_api_response.json()
            request.session['logged_in'] = True
            return redirect('/')
    try:
        request.session.flush()
    except KeyError:
        pass
    return redirect('/')

def logout(request):
    context = {
        'authUrl': AUTH_URL
    }
    request.session.flush()
    return render(request, 'login.html', context)

def renew_token(request):
    if request.session.get('token_expiry', 0) < int(time()):
        return JsonResponse({'error': 'Token already expired'}, status=400)

    files = {
        'grant_type': (None, 'refresh_token'),
        'refresh_token': (None, request.session['refresh_token']),
        'client_id': (None, os.environ['INTRA_UID']),
        'client_secret': (None, os.environ['INTRA_SECRET'])
    }

    try:
        response = requests.post('https://api.intra.42.fr/oauth/token', files=files)
    except requests.RequestException as e:
        return JsonResponse({'error': 'Failed to update status', 'details': str(e)}, status=500)


    if response.status_code == 200:
        json_response = response.json()
        request.session['access_token'] = json_response.get('access_token', None)
        request.session['refresh_token'] = json_response.get('refresh_token', None)
        request.session['token_expiry'] = int(json_response.get('created_at')) + 7200
        return JsonResponse({'message': 'Token renewed successfully'}, status=200)
    else:
        error_message = response.json().get('error', 'intra issue')
        return JsonResponse({'error': error_message}, status=response.status_code)
