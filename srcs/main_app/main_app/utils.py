import json
import requests, logging

from django.db import DatabaseError
from django.db.utils import OperationalError

logger = logging.getLogger(__name__)

def getSessionKey(request, key):
    try:
        return request.session.get(key)
    except OperationalError:
        logger.debug(f'Failed to get session key [{key}]')
        return None
    except:
        logger.debug(f'Failed to get session key [{key}]')
        return None

def setSessionKey(request, key, value):
    try:
        request.session[key] = value
        return True
    except OperationalError:
        logger.debug(f'Failed to save key to session [{key}: {value}]')
        return False
    except:
        logger.debug(f'Failed to save key to session [{key}: {value}]')
        return False

def make_request(request, url, method='get', **kwargs):
    try:
        response = getattr(requests, method)(url, **kwargs)
        response.raise_for_status()
        return (response, False)
    except requests.exceptions.HTTPError as e:
        error_response = {
            "error": f"HTTP Error",
            "status_code": e.response.status_code,
            "url": url,
            "details": e.response.text
        }
        try:
            error_response["message"] = f'{e.response.json()}'
        except:
            error_response["message"] = "Request error"

    except requests.exceptions.ConnectionError:
        error_response = {
            "error": "Connection Error",
            "message": "Failed to connect to the server.",
            "url": url,
            "status_code": 503
        }
    except requests.exceptions.Timeout:
        error_response = {
            "error": "Timeout Error",
            "message": "The request timed out.",
            "url": url,
            "status_code": 504
        }
    except requests.exceptions.RequestException as e:
        error_response = {
            "error": "Request Error",
            "message": str(e),
            "url": url,
            "status_code": 500
        }
    except Exception as e:
        # Handle other exceptions, such as issues with network, or invalid URL
        error_response = {
            "error": "Request Failed",
            "message": str(e),
            "url": url,
            "status_code": 400,  # Indicative of non-HTTP related failures
            "details": "An error occurred that is not an HTTP error."
        }

    setSessionKey(request, 'error', json.dumps(error_response))
    return (None, True)
