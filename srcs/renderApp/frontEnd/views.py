from django.shortcuts import render,redirect
from django.http import HttpResponse
import requests

# Create your views here.

def index(request):
    context = {
        'data':request.session['userData'],
        'blah':"hello World"
    }
    return (render(request, 'main.html' , context))

def login(request):
    files = {
    'grant_type': (None, 'authorization_code'),
    'client_id': (None, 'XXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXX'),
    'client_secret': (None, 'XXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXX'),
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

