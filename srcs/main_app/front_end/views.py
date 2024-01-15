from django.shortcuts import render,redirect
from django.http import HttpResponse
import requests
import environ
import os
from django.template.loader import render_to_string

# Create your views here.

def index(request):
    if 'userData' in request.session:
        context = {
            'data':request.session['userData'],
            'isLoggedIn': True,
            'img': request.session['img'],
            'username': request.session['login'],
            'uid': request.session['uid'],
            'status': request.session['status']

        }
    else:
        context = {
            'isLoggedIn': False,
            'authUrl': environ.Env()('AUTH_URL')
        }
    return (render(request, 'main.html' , context))

def login(request):
    files = {
    'grant_type': (None, 'authorization_code'),
    'client_id': (None, os.environ['INTRA_UID']),
    'client_secret': (None, os.environ['INTRA_SECRET']),
    'code': (None, request.GET.get('code')),
    'redirect_uri': (None, 'http://127.0.0.1:8000/login'),
    }

    # requests.post('user_app/akjs')

    response = requests.post('https://api.intra.42.fr/oauth/token', files=files)
    if response.status_code == 200:
        json_response = response.json()
        access_token = json_response.get('access_token', None)

        if access_token:
            headers = {
                'Authorization': 'Bearer ' + access_token,
            }

            me_response = requests.get('https://api.intra.42.fr/v2/me', headers=headers)
            UID = str(me_response.json()['id'])
            print(access_token)
            print(UID)
            headers = {
                'X-UID': UID,
                'X-TOKEN': access_token

            }
            user_api_response = requests.get(environ.Env()('USER_API_URL') + '/users/api/' + UID, headers=headers)
            print(user_api_response.json())
            request.session['img'] = user_api_response.json()['image']
            request.session['uid'] = user_api_response.json()['uid']
            request.session['login'] = user_api_response.json()['username']
            request.session['status'] = user_api_response.json()['status']
            request.session['access_token'] = access_token
            request.session['userData'] = me_response.json() #this is temporary
            print("Received access token:", access_token)
        else:
            print("Access token not found in the response JSON")

    else:
        print(f"Error: {response.status_code}, {response.text}")



    return redirect('/')

#This will render the template for the logged in state
#This should be called from the main template
#
def homeLoggedIn(request):
    context = {
        
    }
    return HttpResponse(render(request, 'home.html', context))


#This will render the template for the logged in state
#This should be called from the main template
#
def onlineGame(request):
    context = {
        
    }
    x = render_to_string('game.html', context)
    return HttpResponse(x)
