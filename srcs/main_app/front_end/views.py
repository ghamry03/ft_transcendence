from django.shortcuts import render,redirect
from django.http import Http404, HttpResponse, JsonResponse
import requests
import environ
import os
import logging

logger = logging.getLogger(__name__)
# Create your views here.

def index(request):
    if 'logged_in' not in request.session:
        # logger.info('index: LOGGED IN')
        request.session['logged_in'] = False
        context = {}
    else:
        # logger.info('index: NOT LOGGED IN')
        context = {
            'userData':request.session['userData'],
        }
    logging.info('INSIDE INDEX')
    return render(request, 'base.html', context)

def loginPage(request):
    logging.info("LOGIN PAGE")
    if 'logged_in' in request.session and request.session['logged_in'] == True:
        request.session['logged_in'] = False
        request.session.flush()
    context = {
        'authUrl': environ.Env()('AUTH_URL')
    }
    return render(request, 'login.html', context)

def topBar(request):
    if 'logged_in' not in request.session or request.session['logged_in'] == False:
        return render(request, 'topBar.html')

    return render(request, 'topBar.html', {
        'userData': request.session['userData']
    })

def token(request):
    files = {
        'grant_type': (None, 'authorization_code'),
        'client_id': (None, os.environ['INTRA_UID']),
        'client_secret': (None, os.environ['INTRA_SECRET']),
        'code': (None, request.GET.get('code')),
        'redirect_uri': (None, 'http://127.0.0.1:8000/token'),
    }
    response = requests.post('https://api.intra.42.fr/oauth/token', files=files)
    if response.status_code == 200:
        # logger.info('came back from intra')
        json_response = response.json()
        access_token = json_response.get('access_token', None)
        refresh_token = json_response.get('refresh_token', None)
        request.session['access_token'] = access_token
        request.session['refresh_token'] = refresh_token

        if access_token:
            headers = {
                'Authorization': 'Bearer ' + access_token,
            }

            me_response = requests.get('https://api.intra.42.fr/v2/me', headers=headers)
            UID = str(me_response.json()['id'])
            headers = {
                'X-UID': UID,
                'X-TOKEN': access_token

            }
            user_api_response = requests.get(environ.Env()('USER_API_URL') + '/users/api/' + UID, headers=headers)
            request.session['userData'] = user_api_response.json()
            # logger.info('got token successfully')
            request.session['logged_in'] = True
            return redirect("/")
        else:
            logger.info('failed to get token')
    else:
        logger.info('failed to redirect from intra')
    try:
        del request.session["logged_in"]
    except KeyError:
        pass
    request.session.flush()
    raise Http404


from django.core.exceptions import BadRequest
def renew_token(request):
    raise BadRequest('Invalid request.')
    return JsonResponse({
        'message': "Can't refresh_token"
    }, status=404)
    logger.info('loggedin exists')
    logger.info('already logged in')
    files = {
        'grant_type': (None, 'refresh_token'),
        'refresh_token': (None, request.session['refresh_token']),
        'client_id': (None, os.environ['INTRA_UID']),
        'client_secret': (None, os.environ['INTRA_SECRET'])
    }
    response = requests.post('https://api.intra.42.fr/oauth/token', files=files)
    logger.info(response.reason)
    if response.status_code == 200:
        json_response = response.json()
        request.session['access_token'] = json_response.get('access_token', None)
        request.session['refresh_token'] = json_response.get('refresh_token', None)
        logger.info('renewd successfully')
        return HttpResponse()
    request.session.flush()


def homeLoggedIn(request):
    return render(request, 'home.html', {
        'userData': request.session['userData'],
        'logged_in': True
    })
