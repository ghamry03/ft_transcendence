import requests

from main_app.constants import USER_API_URL, FRIEND_API_URL

from django.http import JsonResponse
from django.shortcuts import render


def updateStatus(request, status):
    user_data = request.session.get('userData')
    if not user_data:
        return JsonResponse({'error': 'User data not found'}, status=400)

    uid = user_data.get('uid')
    access_token = request.session.get('access_token')
    if not all([uid, access_token]):
        return JsonResponse({'error': 'Missing UID or access token'}, status=400)

    headers = {
        'X-UID': str(uid),
        'X-TOKEN': str(access_token)
    }
    data = {'status': status}
    try:
        response = requests.post(f"{USER_API_URL}api/user/{uid}/", headers=headers, data=data)
        response.raise_for_status()
    except requests.RequestException as e:
        return JsonResponse({'error': 'Failed to update status', 'details': str(e)}, status=500)

    return JsonResponse({'message': 'Status updated'})

def profile(request, uid):
    user_data = request.session.get('userData')
    access_token = request.session.get('access_token')
    if not all([user_data, access_token]):
        return JsonResponse({'error': 'Authentication required'}, status=401)

    headers = {
        'X-UID': str(user_data['uid']),
        'X-TOKEN': access_token
    }
    try:
        response = requests.get(f"{USER_API_URL}api/user/{uid}", headers=headers)
        response.raise_for_status()
    except requests.RequestException as e:
        return JsonResponse({'error': 'Failed to update status', 'details': str(e)}, status=500)

    profile_data = response.json()

    profile_type = get_profile_type(uid, user_data['uid'], access_token)

    context = {
        'uid': uid,
        'image': profile_data['image'],
        'username': profile_data['username'],
        'full_name': f"{profile_data['first_name']} {profile_data['last_name']}",
        'campus': profile_data['campus_name'],
        'intra_url': profile_data['intra_url'],
        'status': profile_data['status'],
        'type': profile_type,
    }
    return render(request, 'profileContent.html', context)

def get_profile_type(uid, session_uid, access_token):
    if uid != session_uid:
        data = {
            'ownerUID': session_uid,
            'uid': uid,
            'access_token': access_token
        }
        try:
            friends_response = requests.get(f"{FRIEND_API_URL}api/friends/", json=data)
        except requests.RequestException as e:
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
        return JsonResponse({'error': 'Invalid request method'}, status=405)

    user_data = request.session.get('userData')
    access_token = request.session.get('access_token')
    if not user_data or not access_token:
        return JsonResponse({'error': 'Authentication required'}, status=401)

    headers = {
        'X-UID': str(user_data['uid']),
        'X-TOKEN': access_token
    }

    data = request.POST.dict()
    files = request.FILES.dict()

    try:
        response = requests.post(
            f"{USER_API_URL}api/user/{user_data['uid']}/",
            headers=headers, data=data, files=files
        )
        response.raise_for_status()
        request.session['userData'] = response.json()
        return JsonResponse({'message': 'Profile updated successfully'})
    except requests.RequestException as e:
        return JsonResponse({'error': 'Failed to update profile', 'details': str(e)}, status=500)
