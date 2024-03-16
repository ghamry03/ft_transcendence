from django.shortcuts import render
from django.http import HttpResponse, JsonResponse, HttpResponseNotFound
import requests
from . import MEDIA_SERVICE_URL, USER_API_URL


# Create your views here.
def index(request):
    return render(request, 'base.html')

def topBar(request):
    if 'logged_in' not in request.session or request.session['logged_in'] == False:
        return render(request, 'topBar.html')

    return render(request, 'topBar.html', {
        'userData': request.session['userData'],
        'userServiceUrl': MEDIA_SERVICE_URL,
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
    headers = {
        'X-UID': ownerUid,
        'X-TOKEN': token
    }
    response = requests.get(USER_API_URL + '/users/api/' + targetUid, headers=headers)
    opponentInfo = response.json()
    opponentInfo['image'] = MEDIA_SERVICE_URL + opponentInfo['image']
    return JsonResponse(opponentInfo)

def getUnknownUserImg(request):
    response = requests.head(USER_API_URL + '/media/unknownuser.png')
    if response.status_code == 200:
        return HttpResponse(MEDIA_SERVICE_URL + '/media/unknownuser.png')
    return HttpResponseNotFound("The requested resource was not found.")
