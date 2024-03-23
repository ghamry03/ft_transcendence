import socket
from django.http import HttpResponseForbidden

def hostname_whitelist(allowed_hostnames):
    def decorator(view_func):
        def _wrapped_view(request, *args, **kwargs):
            client_ip = request.META.get('REMOTE_ADDR')

            allowed_ips = []
            for hostname in allowed_hostnames:
                try:
                    ip = socket.gethostbyname(hostname)
                    allowed_ips.append(ip)
                except socket.gaierror:
                    # TODO: Handle DNS resolution errors (hostname not found, etc.)
                    continue

            if client_ip not in allowed_ips:
                return HttpResponseForbidden('Access Denied!')
            return view_func(request, *args, **kwargs)
        return _wrapped_view
    return decorator
