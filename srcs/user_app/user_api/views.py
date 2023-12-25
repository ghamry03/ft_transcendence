from django.http import JsonResponse
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from rest_framework import permissions # need to figure out premissions
from .models import User
from .serializers import UserSerializer

# List view of all Users
class UsersListApiView(APIView):
    # TODO: figure it oud
    # permission_classes = [permissions.IsAuthenticated]

    def get(self, request, *args, **kwargs):
        users = User.objects.all().order_by('id') # try
        # users = User.objects.filter(id=request.user.id) #?
        serlializer = UserSerializer(users, many=True)
        return Response(serlializer.data, status=status.HTTP_200_OK)

    def post(self, request, *args, **kwargs):
        # data = {
        #     'id': request.data.get('id'),
        #     'username': request.data.get('username'),
        #     'first_name': request.data.get('first_name'),
        #     'last_name': request.data.get('last_name'),
        # }
        serializer = UserSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class UserDetailApiView(APIView):
    # TODO: figure it oud
    # permission_classes = [permissions.IsAuthenticated]

    def getObjectById(self, user_id):
        try:
            return User.objects.get(id=user_id)
        except User.DoesNotExist:
            return None

    def get(self, requset, user_id, *args, **kwargs):
        user_query = self.getObjectById(user_id)
        if user_query is None:
            return Response(
                {"res", "User with this id does not exist"},
                status=status.HTTP_400_BAD_REQUEST
            )
        serializer = UserSerializer(user_query)
        return Response(serializer.data, status=status.HTTP_200_OK)

    def put(self, request, user_id, *args, **kwargs):
        user_query = self.getObjectById(user_id)
        if not user_query:
            return Response(
                {"res", "User with this id does not exist"},
                status=status.HTTP_400_BAD_REQUEST
            )
        # reqData = {
        #     'id': request.data.get('id'),
        #     'username': request.data.get('username'),
        #     'first_name': request.data.get('first_name'),
        #     'last_name': request.data.get('last_name'),
        # }
        serializer = UserSerializer(
                user_query,
                data=request.data,
                partial=True,  # not working
        )
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_200_OK)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def delete(self, request, user_id, *args, **kwargs):
        user_query = self.getObjectById(user_id)
        if not user_query:
            return Response(
                {"res", "User with this id does not exist"},
                status=status.HTTP_400_BAD_REQUEST,
            )

        user_query.delete()
        return Response(
            {"res", "User deleted"},
            status=status.HTTP_200_OK,
        )

def health_check(request):
    return JsonResponse({'status': 'ok'})