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
        data = {
            'id': request.data.get('id'),
            'username': request.data.get('username'),
            'first_name': request.data.get('first_name'),
            'last_name': request.data.get('last_name'),
        }
        serializer = UserSerializer(data=data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
