import logging

from django.http import JsonResponse

logger = logging.getLogger(__name__)


class HealthCheckMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        if request.path != '/game/health':
            logger.debug('checking database health')

            response = self.handle_health_check(request)
            if response:
                return response

        return self.get_response(request)

    def handle_health_check(self, request):
        from django.db import connections
        from django.db.utils import OperationalError
        db_conn = connections['default']
        try:
            db_conn.cursor()
        except OperationalError:
            logger.debug("can't connect to db")
            return JsonResponse({'error': 'can\'t connect to the db'}, status=503)
        else:
            logger.debug('db connection is alive')
