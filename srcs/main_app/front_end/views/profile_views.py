import json
import requests
from django.http import JsonResponse
from django.shortcuts import render
from main_app.constants import USER_API_URL, FRIEND_API_URL

def updateStatus(request, status):
    headers = {
        'X-UID': str(request.session['userData']['uid']),
        'X-TOKEN': request.session['access_token']
    }
    data = { 'status': status }
    response = requests.post(
            USER_API_URL + 'api/user/' + str(request.session['userData']['uid']) + '/',
            headers=headers,
            data=data
            )
    return JsonResponse({'message': 'status updated'});

def profile(request, uid):
    headers = {
        'X-UID': str(request.session['userData']['uid']),
        'X-TOKEN': request.session['access_token']
    }
    response = requests.get(USER_API_URL + 'api/user/' + str(uid), headers=headers)
    json = response.json()

    profile_type = -1 # Current client profile
    if uid != request.session['userData']['uid']:
        headers = {
            'Content-Type': 'application/json',
        }
        data = {
            'ownerUID': request.session['userData']['uid'],
            'uid': uid,
            'access_token': request.session['access_token']
        }
        friends_response = requests.get(FRIEND_API_URL + 'api/friends/', headers=headers, json=data)
        print(friends_response)
        print(friends_response.json())
        if friends_response:
            friendsJson = friends_response.json()
            if not 'relationship' in friendsJson:
                profile_type = 1
                relationship = -1
            else:
                relationship = int(friendsJson['relationship'])

            if relationship == 0:
                profile_type = 2
            elif relationship == 1:
                initiator = int(friendsJson['initiator'])
                if initiator == 1:
                    profile_type = 3
                elif initiator == 0:
                    profile_type = 4
        else:
            profile_type = -1
        # profile_type = 1 # add friend
        # profile_type = 2 # remove friend
        # profile_type = 3 # cancel request
        # profile_type = 4 # accept request
    else:
        profile_type = 0

    context = {
        'uid': uid,
        'image': json['image'],
        'username': json['username'],
        'full_name': f"{json['first_name']} {json['last_name']}",
        'campus': json['campus_name'],
        'intra_url': json['intra_url'],
        'status': json['status'],
        'type': profile_type,
    }
    return render(request, 'profileContent.html', context)

def edit_profile(request):
    if request.method == 'POST':
        headers = {
            'X-UID': str(request.session['userData']['uid']),
            'X-TOKEN': request.session['access_token']
        }

        data = {}
        files = {}

        username = request.POST.get('username')
        if username:
            data['username'] = username

        image = request.FILES.get('image')
        if image:
            files['image'] = image

        try:
            api_response = requests.post(
                    USER_API_URL + 'api/user/' + str(request.session['userData']['uid']) + '/',
                headers=headers,
                data=data,
                files=files,
            )
        except requests.exceptions.RequestException as e:
            return JsonResponse({'error': 'Failed to connect to the API.', 'details': str(e)}, status=500)

        try:
            response_data = api_response.json()
        except json.JSONDecodeError as e:
            response_data = {'error': 'Failed to pasrse response'}
            return JsonResponse(response_data, status=api_response.status_code)

        if api_response.status_code == 200:
            request.session['userData'] = response_data
            return JsonResponse({'message': 'Form submitted successfully'})

        return JsonResponse(response_data, status=api_response.status_code)
