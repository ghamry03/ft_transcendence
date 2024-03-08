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
    httpResponse.set_cookie('token' , request.session['access_token'])
    return httpResponse
    # return render(request, 'home.html', {
    #     'userData': request.session['userData'],
    # })

def homeCards(request):
    context = {
        'userData': request.session['userData'],
    }
    return render(request, 'homeCards.html', context)

def getOpponentInfo(request):
    ownerUid = request.GET.get('ownerUid')
    targetUid = request.GET.get('targetUid')
    token = request.GET.get('token')
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
    context = {
        'image': json['image'],
        'username': json['username'],
        'full_name': f"{json['first_name']} {json['last_name']}",
        'campus': json['campus_name'],
        'intra_url': json['intra_url']
    }
    return render(request, 'profileContent.html', context)
