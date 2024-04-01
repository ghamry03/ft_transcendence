# friends/views.py
import requests
from rest_framework import generics, status
from rest_framework.response import Response
from django.db.models import Q
from .models import Friend
from .serializers import FriendSerializer
import logging
from . import USER_API_URL
class FriendDetailView(generics.ListCreateAPIView, generics.RetrieveUpdateDestroyAPIView):
    serializer_class = FriendSerializer
    lookup_field = 'id'

    def post(self, request, *args, **kwargs):
        sessionId = request.data.get('session_id', None)
        access_token = request.data.get('access_token', None)
        first_id = request.data.get('first_id', None)

        serializer = FriendSerializer(data=request.data, context={
            'sessionId': sessionId,
            'access_token': access_token,
            'requester_uid': first_id,
            })
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response(serializer.data, status=status.HTTP_201_CREATED)

    def put(self, request, *args, **kwargs):
        first_user = request.data.get('first_user', None)
        second_user = request.data.get('second_user', None)
        relationship = request.data.get('relationship', None)

        obj = Friend.objects.filter(
            Q(first_id=first_user, second_id=second_user) | 
            Q(first_id=second_user, second_id=first_user)
        ).first()

        if not obj:
            return Response({"error": "Friend relationship not found."}, status=status.HTTP_404_NOT_FOUND)
        obj.relationship = int(relationship)
        obj.save()
        return Response(status=status.HTTP_200_OK)

    def delete(self, request, *args, **kwargs):
        first_user = request.data.get('first_user', None)
        second_user = request.data.get('second_user', None)
        flag = request.data.get('clean', None)

        if flag:
            obj = Friend.objects.filter(
                Q(first_id=first_user) | 
                Q(second_id=first_user)).first()
            for record in obj:
                record.delete()
        else:
            obj = Friend.objects.filter(
                Q(first_id=first_user, second_id=second_user) | 
                Q(first_id=second_user, second_id=first_user)).first()
            if not obj:
                return Response({"error": "Friend relationship not found."}, status=status.HTTP_404_NOT_FOUND)
            obj.delete()
        return Response(status=status.HTTP_200_OK)

    def get_user_info(self, owneruid, access_token, uid):
        headers = {
            'X-UID': owneruid,
            'X-TOKEN': access_token
        }
        base_url = f"{USER_API_URL}api/user/{uid}/"

        response = requests.get(base_url, headers=headers)
        if response.status_code != 200:
            return None
        return response.json()

    def get(self, request, *args, **kwargs):
        uid = request.data.get('uid', None)
        access_token = request.data.get('access_token', None)
        ownerUID = request.data.get('ownerUID', None)

        if not uid or not ownerUID:
            return Response(
                {"error": "The 'uid' & 'ownerUID' query parameters are required."},
                status=status.HTTP_400_BAD_REQUEST
            )

        if uid == ownerUID:
            try:
                queryset = Friend.objects.filter(Q(first_id=ownerUID) | Q(second_id=ownerUID))
            except:
                return Response(data = {}, status=status.HTTP_200_OK)
            friendsList = []
            friendRequests = 0;
            for friend in queryset:
                if f'{friend.first_id}' == ownerUID:
                    target = friend.second_id
                else:
                    target = friend.first_id
                resp = self.get_user_info(ownerUID, access_token, target)
                if resp:
                    resp['relationship'] = friend.relationship
                    resp['image'] = f'{resp['image']}'
                    if (f'{friend.first_id}' == ownerUID):
                        resp["initiator"] = 1
                    else:
                        if friend.relationship == 1:
                            friendRequests += 1
                        resp["initiator"] = 0
                    friendsList.append(resp)
            data = {"friendsList": friendsList, "friendRequests": friendRequests}
        else:
            '''
                curl -X GET -H "Content-Type: application/json" -d '{
                    "uid": "123", "ownerUID":"123" ,  "access_token": "xxxxxxxxxxx"}' /api/friends/ 
            '''
            try:
                obj = Friend.objects.filter(
                    Q(first_id=uid, second_id=ownerUID) |
                    Q(first_id=ownerUID, second_id=uid)
                ).first()
            except:
                return Response(data = {}, status=status.HTTP_200_OK)
            if not obj:
                return Response(data = {}, status=status.HTTP_200_OK)
            data = {
                'relationship': obj.relationship,
                'initiator': 0
            }
            if int(obj.first_id) == int(ownerUID):
                data['initiator'] = 1
            else:
                data['initiator'] = 0
        return Response(data, status=status.HTTP_200_OK)
