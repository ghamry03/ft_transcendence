from django.http import JsonResponse
import logging

logger = logging.getLogger(__name__)

class HealthCheckMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        if request.path == '/health-check/':
            return self.handle_health_check(request)
        return self.get_response(request)

    def handle_health_check(self, request):
        from django.db import connections
        from django.db.utils import OperationalError
        logger.debug("we are here")
        db_conn = connections['default']
        logger.debug("we are here")
        try:
            db_conn.cursor()
        except OperationalError:
            db_alive = False
        else:
            db_alive = True

        health_status = {
            'database': 'OK' if db_alive else 'ERROR',
        }
        return JsonResponse(health_status)
