from django.http import Http404, JsonResponse
from rest_framework.views import APIView
from rest_framework import exceptions
from rest_framework.response import Response
from rest_framework import status
from .models import User, FtUser
from .serializers import UserSerializer
from user_app.permissions import IsRequestedUser
from django.core.exceptions import ValidationError
from django.db.models import Q

# List view of all Users
class UsersListApiView(APIView):
    def get(self, request):
        """
            curl -X GET -H "X-UID: {UID}" -H "X-TOKEN: {TOKEN}"         \
                    {URL}/api/users/
        """
        users = User.objects.all().order_by('uid')
        serializer = UserSerializer(users, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)

    def post(self, request):
        print(request.data)
        """
            curl -X POST -H "X-UID: {UID}" -H "X-TOKEN: {TOKEN}"        \
                    -F "uid={NEW_USER}" -F "username={NEW_USERNAME}"    \
                    -F "image=@{IMG_PATH}"                              \
                    {URL}/api/users/
        """
        serializer = UserSerializer(data=request.data)

        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response(serializer.data, status=status.HTTP_201_CREATED)

class UserDetailApiView(APIView):
    permission_classes = (IsRequestedUser,)
    # authentication_classes = ()

    def getObjectById(self, user_id):
        try:
            return User.objects.get(uid=user_id)
        except User.DoesNotExist:
            raise exceptions.NotFound

    def get(self, request, user_id):
        """
            curl -X GET -H "X-UID: {UID}" -H "X-TOKEN: {TOKEN}"         \
                    {URL}/api/user/{TARGET_USER}
        """
        try:
            user_query = self.getObjectById(user_id)

        except:
            req_uid = request.META.get('HTTP_X_UID')
            req_token = request.META.get('HTTP_X_TOKEN')
            if int(req_uid) == user_id:
                try:
                    user_query = FtUser(access_token=req_token)
                    user_query.save()
                except ValidationError as e:
                    return Response(e.messages, status=status.HTTP_400_BAD_REQUEST)
            else:
                raise Http404
        serializer = UserSerializer(user_query)
        return Response(serializer.data, status=status.HTTP_200_OK)

    def post(self, request, user_id):
        """
            curl -X POST -H "X-UID: {UID}" -H "X-TOKEN: {TOKEN}"        \
                    -F "uid={NEW_USER}" -F "username={NEW_USERNAME}"    \
                    -F "image=@{IMG_PATH}"                              \
                    {URL}/api/user/{TARGET_USER}
        """
        user_query = self.getObjectById(user_id)
        serializer = UserSerializer(
                user_query,
                data=request.data,
                partial=True,
        )
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response(serializer.data, status=status.HTTP_200_OK)

    def delete(self, request, user_id):
        """
            curl -X DELETE -H "X-UID: {UID}" -H "X-TOKEN: {TOKEN}"        \
                    {URL}/api/user/{TARGET_USER}
        """
        user_query = self.getObjectById(user_id)
        user_query.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)

class UserSearch(APIView):
    def get(self, request, pattern):
        users = User.objects.filter(
            Q(username__icontains=pattern)
            | Q(first_name__icontains=pattern)
            | Q(last_name__icontains=pattern)
        )
        serializer = UserSerializer(users, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)


def health_check(request):
    return JsonResponse({'status': 'ok'})
