from django.shortcuts import render,redirect
from django.http import HttpResponse
import requests

# Create your views here.

def index(request):
    if 'userData' in request.session:
        context = {
            'data':request.session['userData'],
            'isLoggedIn': True
        }
    else:
        context = {
            'isLoggedIn': False

        }
    return (render(request, 'main.html' , context))

def login(request):
    files = {
    'grant_type': (None, 'authorization_code'),
    'client_id': (None, 'u-s4t2ud-0ddaf921e5492df40a174c01c6e982998ac8a8405a4f53a5066bc62006e749b7'),
    'client_secret': (None, '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'),
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
