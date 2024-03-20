import json
import requests
from django.http import JsonResponse
from django.shortcuts import render
from main_app.constants import USER_API_URL

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

    profile_type = 0 # Current client profile
    if uid != request.session['userData']['uid']:
        # check if it's a friend or not
        profile_type = 1 # a friend
        profile_type = 2 # not a friend

    context = {
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
