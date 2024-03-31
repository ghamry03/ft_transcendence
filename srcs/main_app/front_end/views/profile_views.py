from main_app.utils import getSessionKey, make_request
from main_app.constants import USER_API_URL, FRIEND_API_URL
from .home_views import getTournamentHistory, getMatchHistory

from django.http import JsonResponse
from django.shortcuts import render


def updateStatus(request, status):
    user_data = getSessionKey(request, 'userData')
    if not user_data:
        return JsonResponse({'error': 'check /errors to retrive error'}, status=400)

    uid = user_data.get('uid', None) if user_data else None

    access_token = getSessionKey(request, 'access_token')
    if not all([uid, access_token]):
        return JsonResponse({'error': 'Missing UID or access token'}, status=400)

    headers = {
        'X-UID': str(uid),
        'X-TOKEN': str(access_token)
    }
    data = {'status': status}
    response, isError = make_request(request, f"{USER_API_URL}api/user/{uid}/", headers=headers, data=data)
    if isError:
        return JsonResponse({'error': 'check /errors to retrive error'}, status=400)

    return JsonResponse({'message': 'Status updated'})

def profile(request, uid):
    user_data = getSessionKey(request, 'userData')
    access_token = getSessionKey(request, 'access_token')
    if not all([user_data, access_token]):
        return JsonResponse({'error': 'Authentication required'}, status=401)

    headers = {
        'X-UID': str(uid),
        'X-TOKEN': access_token
    }
    response, isError = make_request(request, f"{USER_API_URL}api/user/{uid}", headers=headers)
    if isError:
        return JsonResponse({'error': 'check /errors to retrive error'}, status=400)

    profile_data = response.json()

    profile_type = get_profile_type(request, uid, user_data['uid'], access_token)

    tournamentHistory = getTournamentHistory(request, uid)
    matchHistory = getMatchHistory(request, uid)

    context = {
        'uid': uid,
        'image': profile_data['image'],
        'username': profile_data['username'],
        'full_name': f"{profile_data['first_name']} {profile_data['last_name']}",
        'campus': profile_data['campus_name'],
        'intra_url': profile_data['intra_url'],
        'status': profile_data['status'],
        'type': profile_type,
        'tournamentHistory': tournamentHistory,
        'matchHistory': matchHistory
    }
    return render(request, 'profileContent.html', context)

def get_profile_type(request, uid, session_uid, access_token):
    if uid != session_uid:
        data = {
            'ownerUID': session_uid,
            'uid': uid,
            'access_token': access_token
        }
        friends_response, isError = make_request(request, f"{FRIEND_API_URL}api/friends/", json=data)
        if isError:
            return -1

        if friends_response.ok:
            friends_data = friends_response.json()
            relationship = friends_data.get('relationship', -1)
            return determine_relationship_type(relationship, friends_data)
        return -1

    return 0

def determine_relationship_type(relationship, friends_data):
    """Maps relationship status to profile type."""
    if relationship == 0:
        return 2  # remove friend
    elif relationship == 1:
        initiator = int(friends_data.get('initiator', -1))
        if initiator == 1:
            return 3  # cancel request
        elif initiator == 0:
            return 4  # accept request
    return 1  # add friend

def edit_profile(request):
    if request.method != 'POST':
        return JsonResponse({'error': 'check /errors to retrive error'}, status=400)

    user_data = getSessionKey(request, 'userData')
    access_token = getSessionKey(request, 'access_token')
    if not user_data or not access_token:
        return JsonResponse({'error': 'check /errors to retrive error'}, status=400)

    headers = {
        'X-UID': str(user_data['uid']),
        'X-TOKEN': access_token
    }

    data = {}
    files = {}

    username = request.POST.get('username', None)
    if username:
        data['username'] = username

    image = request.FILES.get('image', None)
    if image:
        files['image'] = image

    response, isError = make_request(
            request,
            f"{USER_API_URL}api/user/{user_data['uid']}/",
            method='post', headers=headers, data=data, files=files
    )
    if isError:
        return JsonResponse({'error': 'check /errors to retrive error'}, status=400)
    request.session['userData'] = response.json()
    return JsonResponse({'message': 'Profile updated successfully'})
