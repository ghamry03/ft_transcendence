import logging

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
