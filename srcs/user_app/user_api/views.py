from django.http import Http404, JsonResponse
from rest_framework.views import APIView
from rest_framework import exceptions
from rest_framework.response import Response
from rest_framework import status
from .models import User
from .serializers import UserSerializer
from user_app.permissions import IsRequestedUser
from os import remove

# List view of all Users
class UsersListApiView(APIView):
    def get(self, request):
        """
            curl -X GET -H "X-UID: {UID}" -H "X-TOKEN: {TOKEN}"         \
                    {URL}/users/api/
        """
        users = User.objects.all().order_by('uid')
        serlializer = UserSerializer(users, many=True)
        return Response(serlializer.data, status=status.HTTP_200_OK)

    def post(self, request):
        """
            curl -X POST -H "X-UID: {UID}" -H "X-TOKEN: {TOKEN}"        \
                    -F "uid={NEW_USER}" -F "username={NEW_USERNAME}"    \
                    -F "image=@{IMG_PATH}"                              \
                    {URL}/users/api/
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
            curl -X GET -H "X-UID: {UID}" -H "X-TOKEN: {TOKEN}" \
                    {URL}/users/api/{TARGET_USER}
        """
        try:
            user_query = self.getObjectById(user_id)
        except:
            req_uid = request.META.get('HTTP_X_UID')
            req_token = request.META.get('HTTP_X_TOKEN')
            if int(req_uid) == user_id:
                user_query = User()
                user_query.oaut_42_user(req_token)
            else:
                raise Http404
        serializer = UserSerializer(user_query)
        return Response(serializer.data, status=status.HTTP_200_OK)

    def post(self, request, user_id):
        """
            curl -X POST -H "X-UID: {UID}" -H "X-TOKEN: {TOKEN}"        \
                    -F "uid={NEW_USER}" -F "username={NEW_USERNAME}"    \
                    -F "image=@{IMG_PATH}"                              \
                    {URL}/users/api/{TARGET_USER}
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
        # TODO: fix a bug where the admin page delete isn't deleting the image, (MOST PROB the MEDIA)
        """
            curl -X POST -H "X-UID: {UID}" -H "X-TOKEN: {TOKEN}"        \
                    {URL}/users/api/{TARGET_USER}
        """
        user_query = self.getObjectById(user_id)
        remove('media/' + str(user_query.image))
        user_query.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)

def health_check(request):
    return JsonResponse({'status': 'ok'})