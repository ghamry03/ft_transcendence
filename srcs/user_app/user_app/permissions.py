from rest_framework import permissions
from rest_framework import exceptions
from user_api.models import User

class IsRequestedUser(permissions.BasePermission):
    def UserExist(self, requested_uid):
        try:
            User.objects.get(uid=requested_uid)
        except User.DoesNotExist:
            return False
        return True

    def has_permission(self, request, view):
        req_user = request.META.get('HTTP_X_UID')
        views_user = view.kwargs['user_id']
        if not req_user or not views_user:
            raise exceptions.ParseError
        user = int(req_user)
        requested_user = int(views_user)
        if request.method == 'GET':
            if self.UserExist(requested_user):
                return True
            elif user != requested_user:
                print("huh 2")
                raise exceptions.PermissionDenied
        elif user != requested_user:
            print(user, requested_user)
            print("huh 3")
            raise exceptions.PermissionDenied
        return True
