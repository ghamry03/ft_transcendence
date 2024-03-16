from django.shortcuts import render
from django.http import HttpResponse, JsonResponse
import requests
import json
from . import USER_API_URL

# Create your views here.
def index(request):
    return render(request, 'base.html')

def topBar(request):
    if 'logged_in' not in request.session or request.session['logged_in'] == False:
        return render(request, 'topBar.html')

    return render(request, 'topBar.html', {
        'userData': request.session['userData']
    })

def homePage(request):
    context = {
        'userData' : request.session['userData'],
    }

    httpResponse = HttpResponse(render(request, 'home.html', context))
    httpResponse.set_cookie('uid' , request.session['userData']['uid'])
    return httpResponse

def homeCards(request):
    context = {
        'userData': request.session['userData'],
    }
    return render(request, 'homeCards.html', context)

def getOpponentInfo(request):
    ownerUid = request.GET.get('ownerUid')
    targetUid = request.GET.get('targetUid')
    token = request.session['access_token']
    # token = request.GET.get('token')
    headers = {
        'X-UID': ownerUid,
        'X-TOKEN': token
    }
    opponentInfo = requests.get('http://userapp:3000/users/api/' + targetUid, headers=headers)
    return JsonResponse(opponentInfo.json())

def profile(request, uid):
    headers = {
        'X-UID': str(request.session['userData']['uid']),
        'X-TOKEN': request.session['access_token']
    }
    response = requests.get(USER_API_URL + '/users/api/' + str(uid), headers=headers)
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
        'type': profile_type
    }
    return render(request, 'profileContent.html', context)

def updateStatus(request, status):
    headers = {
        'X-UID': str(request.session['userData']['uid']),
        'X-TOKEN': request.session['access_token']
    }
    data = { 'status': status }
    response = requests.post(
        USER_API_URL + '/users/api/' + str(request.session['userData']['uid']) + '/',
        headers=headers,
        data=data
    )
    return JsonResponse({'message': 'status updated'});

def edit_profile(request):
    print(request)
    if request.method == 'POST':
        # print(pretty_request(request))
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
                    USER_API_URL + '/users/api/' + str(request.session['userData']['uid']) + '/',
                headers=headers,
                data=data,
                files=files,
            )
        except requests.exceptions.RequestException as e:
            return JsonResponse({'error': 'Failed to connect to the API.', 'details': str(e)}, status=500)


        print("1")
        try:
            response_data = api_response.json()
        except json.JSONDecodeError as e:
            response_data = {'error': 'Failed to pasrse response'}
            print("1.5")
            return JsonResponse(response_data, status=api_response.status_code)

        print("2")
        if api_response.status_code == 200:
            request.session['userData'] = response_data
            return JsonResponse({'message': 'Form submitted successfully'})

        print("3")
        return JsonResponse(response_data, status=api_response.status_code)

    else:
        return render(request, 'editProfileContent.html')
