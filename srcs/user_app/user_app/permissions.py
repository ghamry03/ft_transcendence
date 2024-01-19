from rest_framework import permissions
from user_api.models import User

class IsRequestedUser(permissions.BasePermission):
    def UserExist(self, requested_uid):
        try:
            User.objects.get(uid=requested_uid)
        except User.DoesNotExist:
            return False
        return True

    def has_permission(self, request, view):
        user = int(request.META.get('HTTP_X_UID'))
        requested_user = int(view.kwargs['user_id'])
        if not user or not requested_user:
            return False
        if request.method == 'GET':
            if self.UserExist(requested_user):
                return True
            else:
                return user == requested_user
        else:
            return user == requested_user
