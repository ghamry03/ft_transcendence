import json
import requests
import logging

from main_app.utils import getSessionKey, setSessionKey, make_request
from main_app.constants import USER_API_URL
from front_end.hostnameAuthentication import hostname_whitelist
from django.db.utils import OperationalError

from django.conf import settings
from django.views.generic import View
from django.utils.decorators import method_decorator
from django.http import JsonResponse, HttpResponseNotFound, HttpResponseBadRequest, HttpResponseNotFound
from django.contrib.sessions.models import Session
from django.db import connections

logger = logging.getLogger(__name__)

@method_decorator(hostname_whitelist(settings.ALLOWED_HOSTNAMES_FOR_API), name='dispatch')
class SessionDataView(View):
    def get(self, request, *args, **kwargs):
        session_id = request.GET.get('sessionID')
        if not session_id:
            return HttpResponseBadRequest('The sessionID parameter is required.')

        try:
            session = Session.objects.get(session_key=session_id)
            session_data = session.get_decoded()
        except Session.DoesNotExist:
            return HttpResponseNotFound('Session data not found.')

        return JsonResponse({'sessionData': session_data})

def getOpponentInfo(request):
    ownerUid = request.GET.get('ownerUid')
    targetUid = request.GET.get('targetUid')
    access_token = getSessionKey(request, 'access_token')
    headers = {
        'X-UID': ownerUid,
        'X-TOKEN': access_token
    }
    response, isError = make_request(request, USER_API_URL + 'api/user/' + targetUid, headers=headers)
    if isError:
        return JsonResponse({'error': 'check /errors to retrive error'}, status=400)

    try:
        opponentInfo = response.json()
    except requests.exceptions.JSONDecodeError as e:
        return JsonResponse({'error': 'Failed to parse opponent info', 'details': str(e)}, status=400)

    opponentInfo['image'] = opponentInfo['image']
    return JsonResponse(opponentInfo)

def errors(request):
    try:
        db_conn = connections['default']
        db_conn.cursor()
    except OperationalError:
        error_response = {
            "error": "Connection Error",
            "message": "Failed to connect to the server.",
            "url": 'postgres',
            "status_code": 503
        }
        return JsonResponse(error_response, status=error_response['status_code'])
    except:
        error_response = {
            "error": "Connection Error",
            "message": "Failed to connect to the server.",
            "url": 'postgres',
            "status_code": 503
        }
        return JsonResponse(error_response, status=int( error_response['status_code'] ))


    error = getSessionKey(request, 'error')
    request.session.pop('error', None)
    request.session.save()
    logger.debug(error)

    if error:
        error_json = json.loads(error)
        return JsonResponse(error_json, status=int( error_json['status_code'] ))

    return JsonResponse({'error': 'no error'}, status=200)
