from rest_framework import permissions

class IsRequestedUser(permissions.BasePermission):
    def has_permission(self, request, view):
        user = int(request.META.get('HTTP_X_UID'))
        requested_user = int(view.kwargs['user_id'])
        if not user or not requested_user:
            return False
        return user == requested_user
