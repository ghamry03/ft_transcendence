# friends/views.py
from rest_framework import generics
from django.shortcuts import get_object_or_404
from django.db.models import Q
from friends_api.models import Friend
from friends_api.serializers import FriendSerializer
from django.http import Http404

class FriendDetailView(generics.ListCreateAPIView, generics.RetrieveUpdateDestroyAPIView):
    serializer_class = FriendSerializer
    lookup_field = 'id'

    def get_queryset(self):
        id = self.request.data.get('id')
        op_type = self.request.data.get('type')

        if op_type == 1:
            if id is not None:
                try:
                    return Friend.objects.filter(Q(first_id=int(id)) | Q(second_id=int(id)))
                except ValueError:
                    raise Http404("Invalid uid format")
            else:
                return Friend.objects.all()
        elif op_type == 2:
            try:
                return Friend.objects.filter(pk=int(id))
            except (Friend.DoesNotExist, ValueError):
                raise Http404("Friend not found or invalid uid format")
        else:
            raise Http404("Operation type is required")
        
    def get_object(self):
        queryset = self.get_queryset()
        lookup_value = self.request.data.get("id")
        obj = get_object_or_404(queryset, **{self.lookup_field: lookup_value})
        return obj

    def perform_create(self, serializer):
        serializer.save()
