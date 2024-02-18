from django.shortcuts import render,redirect
from django.http import HttpResponse
import requests
import environ
import os
from . import AUTH_URL, USER_API_URL

# Create your views here.

def index(request):
    if 'userData' in request.session:
        context = {
            'userData':request.session['userData'],
            'isLoggedIn': True
        }
    else:
        context = {
            'isLoggedIn': False,
            'authUrl': AUTH_URL
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
            user_api_response = requests.get(USER_API_URL + '/users/api/' + UID, headers=headers)
            print(user_api_response.status_code)
            request.session['userData'] = user_api_response.json()
            request.session['access_token'] = access_token
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
        'userData' : request.session['userData']
    }

    httpResponse = HttpResponse(render(request, 'home.html', context))
    # httpResponse.set_cookie('uid' , request.session['uid'])
    httpResponse.set_cookie('token' , request.session['access_token'])
    return httpResponse
