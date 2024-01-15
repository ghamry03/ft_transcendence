from django.http import Http404, JsonResponse
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from .models import User
from .serializers import UserSerializer
from user_app.permissions import IsRequestedUser

# List view of all Users
class UsersListApiView(APIView):
    def get(self, request):
        """
            curl -X GET -H "X-UID: {UID}" -H "X-TOKEN: {TOKEN}" \
            http://localhost:8001/users/api/
        """
        users = User.objects.all().order_by('uid')
        serlializer = UserSerializer(users, many=True)
        return Response(serlializer.data, status=status.HTTP_200_OK)

    def post(self, request):
        serializer = UserSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

class UserDetailApiView(APIView):
    permission_classes = (IsRequestedUser,)

    def getObjectById(self, user_id):
        try:
            return User.objects.get(uid=user_id)
        except User.DoesNotExist:
            raise Http404

    def get(self, request, user_id):
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

    def put(self, request, user_id):
        user_query = self.getObjectById(user_id)
        serializer = UserSerializer(
                user_query,
                data=request.data,
                partial=True,
        )
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_200_OK)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def delete(self, request, user_id):
        user_query = self.getObjectById(user_id)
        user_query.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)

def health_check(request):
    return JsonResponse({'status': 'ok'})