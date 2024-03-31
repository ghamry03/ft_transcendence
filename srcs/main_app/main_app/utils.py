import json
import requests, logging

from django.db import DatabaseError

logger = logging.getLogger(__name__)

def getSessionKey(request, key):
    try:
        return request.session.get(key)
    except:
        logger.debug(f'Failed to get session key [{key}]')
        return None

def setSessionKey(request, key, value):
    try:
        request.session[key] = value
        return True
    except:
        logger.debug(f'Failed to save key to session [{key}: {value}]')
        return False

def make_request(request, url, method='get', **kwargs):
    response = {}
    try:
        response = getattr(requests, method)(url, **kwargs)
        response.raise_for_status()
        return (response, False)
    except requests.exceptions.HTTPError as e:
        error_response = {
            "error": "HTTP Error",
            "message": str(e),
            "status_code": response.get('status_code', 400),
            "details": response.get('text', '')
        }
    except requests.exceptions.ConnectionError:
        error_response = {
            "error": "Connection Error",
            "message": "Failed to connect to the server.",
            "status_code": 503
        }
    except requests.exceptions.Timeout:
        error_response = {
            "error": "Timeout Error",
            "message": "The request timed out.",
            "status_code": 504
        }
    except requests.exceptions.RequestException as e:
        error_response = {
            "error": "Request Error",
            "message": str(e),
            "status_code": 500
        }
    setSessionKey(request, 'error', json.dumps(error_response))
    return (response, True)
