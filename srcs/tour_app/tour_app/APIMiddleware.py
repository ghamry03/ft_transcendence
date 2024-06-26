import logging

from django.http import JsonResponse
from django.db import connections
from django.db.utils import OperationalError

logger = logging.getLogger(__name__)


class HealthCheckMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        if request.path != '/tour/health':
            logger.debug(f'checking database health [{request.path}]')

            response = self.handle_health_check(request)
            if response:
                return response

        return self.get_response(request)

    def handle_health_check(self, request):
        db_conn = connections['default']
        try:
            db_conn.cursor()
        except OperationalError:
            logger.debug(f"can't connect to db [{request.path}]")
            return JsonResponse({'error': f'can\'t connect to the db [{request.path}]'}, status=503)
        else:
            logger.debug(f'db connection is alive [{request.path}]')
