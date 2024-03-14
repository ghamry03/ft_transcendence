from django.shortcuts import render
from django.http import HttpResponse, JsonResponse
import requests
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

def pretty_request(request):
    headers = ''
    for header, value in request.META.items():
        if not header.startswith('HTTP'):
            continue
        header = '-'.join([h.capitalize() for h in header[5:].lower().split('_')])
        headers += '{}: {}\n'.format(header, value)

    return (
        '{method} HTTP/1.1\n'
        'Content-Length: {content_length}\n'
        'Content-Type: {content_type}\n'
        '{headers}\n\n'
        '{body}'
    ).format(
        method=request.method,
        content_length=request.META['CONTENT_LENGTH'],
        content_type=request.META['CONTENT_TYPE'],
        headers=headers,
        body=request.body,
    )

def edit_profile(request):
    print(request)
    if request.method == 'POST':
        # print(pretty_request(request))
        headers = {
            'X-UID': str(request.session['userData']['uid']),
            'X-TOKEN': request.session['access_token']
        }
        data = None
        files = None
        print("username: " + request.POST.get('username'))
        if request.POST.get('username'):
            data = { 'username': request.POST.get('username') }
        if request.FILES.get('image'):
            print("IMAGE MAWGOOOOD")
            files = { 'image': request.FILES.get('image') }
        response = requests.post(
            USER_API_URL + '/users/api/' + str(request.session['userData']['uid']) + '/',
            headers=headers,
            data=data,
            files=files,
        )
        # pretty_request(response)
        return render(request, 'editProfileContent.html')
        # return JsonResponse({'message': 'Form submitted successfully!'})
    else:
        return render(request, 'editProfileContent.html')
