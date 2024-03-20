import requests

from front_end.hostnameAuthentication import hostname_whitelist
from main_app.constants import USER_API_URL, MEDIA_SERVICE_URL

from django.conf import settings
from django.views.generic import View
from django.utils.decorators import method_decorator
from django.http import HttpResponse, JsonResponse, HttpResponseNotFound, HttpResponseBadRequest, HttpResponseNotFound
from django.contrib.sessions.models import Session


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
    token = request.session['access_token']
    headers = {
        'X-UID': ownerUid,
        'X-TOKEN': token
    }
    response = requests.get(USER_API_URL + 'api/user/' + targetUid, headers=headers)
    opponentInfo = response.json()
    opponentInfo['image'] = opponentInfo['image']
    return JsonResponse(opponentInfo)

def getUnknownUserImg(request):
    response = requests.head(USER_API_URL + '/media/unknownuser.png')
    if response.status_code == 200:
        return HttpResponse(MEDIA_SERVICE_URL + '/media/unknownuser.png')
    return HttpResponseNotFound("The requested resource was not found.")
