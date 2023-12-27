from django.http import Http404
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from .models import User
from .serializers import UserSerializer

# List view of all Users


class UsersListApiView(APIView):
    def get(self, request, formant=None):
        users = User.objects.all().order_by('id')
        serlializer = UserSerializer(users, many=True)
        return Response(serlializer.data, status=status.HTTP_200_OK)

    def post(self, request, formant=None):
        serializer = UserSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class UserDetailApiView(APIView):
    def getObjectById(self, user_id):
        try:
            return User.objects.get(id=user_id)
        except User.DoesNotExist:
            raise Http404
            # raise Response(
            #     {"res", "User with this id does not exist"},
            #     status=status.HTTP_400_BAD_REQUEST,
            # )

    def get(self, requset, user_id, formant=None):
        user_query = self.getObjectById(user_id)
        serializer = UserSerializer(user_query)
        return Response(serializer.data, status=status.HTTP_200_OK)

    def put(self, request, user_id, formant=None):
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

    def delete(self, request, user_id, formant=None):
        user_query = self.getObjectById(user_id)
        user_query.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)
