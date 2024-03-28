import requests, logging

from main_app.utils import getSessionKey
from main_app.constants import FRIEND_API_URL, USER_API_URL

from django.shortcuts import render
from django.http import HttpResponse, JsonResponse


logger = logging.getLogger(__name__)

def searchUsers(request, username):
    userData = getSessionKey(request, 'userData')
    uid = userData.get('uid', None) if userData else None
    access_token = getSessionKey(request, 'access_token')
    headers = {
        'X-UID': uid,
        'X-TOKEN': access_token
    }

    base_url = USER_API_URL + 'api/search/' + username

    try:
        response = requests.get(base_url, headers=headers)
    except requests.RequestException as e:
        return JsonResponse({'error': 'Failed to update status', 'details': str(e)}, status=500)

    if response.status_code == 200:
        data = {
            'status': response.status_code,
            'data': response.json(),
            'uid': userData.get('uid', None)
            }
        logger.debug(data)
        return render(request, 'searchedUser.html', data)
    else:
        logger.debug(f"Error: {response.status_code}")
        return HttpResponse()

def addUser(request, friendUID):
    headers = { 'Content-Type': 'application/json' }
    userData = getSessionKey(request, 'userData')
    access_token = getSessionKey(request, 'access_token')
    session_id = getSessionKey(request, 'session_key')

    myuid = userData.get('uid', None) if userData else None

    try:
        response = requests.post(
            FRIEND_API_URL + "api/friends/",
            headers=headers,
            json={
                "first_id": f'{myuid}',
                "second_id": f'{friendUID}',
                "session_id": session_id,
                "access_token": access_token,
                },
        )
        response.raise_for_status()
    except requests.RequestException as e:
        return JsonResponse({'error': 'Failed to update status', 'details': str(e)}, status=500)
    return JsonResponse(data={})

def acceptFriend(request, friendUID):
    headers = { 'Content-Type': 'application/json' }
    userData = getSessionKey(request, 'userData')
    access_token = getSessionKey(request, 'access_token')
    session_id = getSessionKey(request, 'session_key')

    myuid = userData.get('uid', None) if userData else None

    try:
        response = requests.put(
            FRIEND_API_URL + "api/friends/",
            headers=headers,
            json={
                "first_user": f'{myuid}',
                "second_user": f'{friendUID}',
                "relationship": 0, 
                "session_id": session_id, 
                "access_token": access_token,
                },
        )
        response.raise_for_status()
    except requests.RequestException as e:
        return JsonResponse({'error': 'Failed to update status', 'details': str(e)}, status=500)
    return JsonResponse(data={})


def rejectFriend(request, friendUID):
    headers = { 'Content-Type': 'application/json' }
    userData = getSessionKey(request, 'userData')
    access_token = getSessionKey(request, 'access_token')
    session_id = getSessionKey(request, 'session_key')

    myuid = userData.get('uid', None) if userData else None

    try:
        response = requests.delete(
                FRIEND_API_URL + "api/friends/",
                headers=headers,
                json={
                    "first_user": f'{myuid}',
                    "second_user": f'{friendUID}',
                    "session_id": session_id,
                    "access_token": access_token,
                    },
                )
        response.raise_for_status()
    except requests.RequestException as e:
        return JsonResponse({'error': 'Failed to update status', 'details': str(e)}, status=500)

    return JsonResponse(data={})
