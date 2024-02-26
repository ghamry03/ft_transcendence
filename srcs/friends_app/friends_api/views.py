# friends/views.py
from rest_framework import generics
from django.shortcuts import get_object_or_404
from django.db.models import Q
from .models import Friend
from .serializers import FriendSerializer
from django.http import Http404
from .exceptions import BadRequest, NotFound



class FriendDetailView(generics.ListCreateAPIView, generics.RetrieveUpdateDestroyAPIView):
    serializer_class = FriendSerializer
    lookup_field = 'id'
    
    def getFriendList(self, id):
        print("in here")
        try:
            obj = Friend.objects.filter(Q(first_id=int(id)) | Q(second_id=int(id)))
            return obj
        except ValueError:
            raise BadRequest(detail="bad request: `id` must be a number")
        except TypeError:
            raise BadRequest(detail="bad request: `id` is required")
        
    def getFriendRecordByPK(self, id):
        try:
            return Friend.objects.filter(pk=id)
        except (Friend.DoesNotExist, ValueError):
            raise BadRequest(detail="bad request: `id` must be a number")
        
    def getFriendRecordByUID(self, id):
        id2 = self.request.data.get('second_id')
        try:
            return Friend.objects.filter((Q(first_id=int(id)) & Q(second_id=int(id2))) | (Q(first_id=int(id2)) & Q(second_id=int(id))))
        except ValueError:
            raise BadRequest(detail="bad request: `id` & `second_id` must be numbers.")


    def get_queryset(self):
        id = self.request.data.get('id')
        op_type = self.request.data.get('type')

        operations = {
            1: self.getFriendList,
            2: self.getFriendRecordByPK,
            3: self.getFriendRecordByUID
        }

        filter_op = operations.get(op_type)

        if filter_op is not None:
            return filter_op(id)
        else:
            raise BadRequest(detail="bad request: `type` must be one of the following 1 | 2 | 3")

        # if op_type == 1:
        #     if id is not None:
        #         try:
        #             obj = Friend.objects.filter(Q(first_id=int(id)) | Q(second_id=int(id)))
        #             return obj
        #         except ValueError:
        #             raise BadRequest(detail="bad request: `id` must be a number")
        #     else:
        #         return Friend.objects.all()
        # elif op_type == 2:
        #     try:
        #         return Friend.objects.filter(pk=id)
        #     except (Friend.DoesNotExist, ValueError):
        #         raise BadRequest(detail="bad request: `id` must be a number")
        # elif op_type ==3:
        #     id2 = self.request.data.get('second_id')
        #     if id is not None and id2 is not None:
        #         try:
        #             return Friend.objects.filter((Q(first_id=int(id)) & Q(second_id=int(id2))) | (Q(first_id=int(id2)) & Q(second_id=int(id))))
        #         except ValueError:
        #             raise BadRequest(detail="bad request: `id` & `second_id` must be numbers.")
        #     else:
        #         return Friend.objects.all()
        # elif op_type is None:
        #     raise BadRequest(detail="bad request: `id` & `second_id` are required for this operation.")
        # else:
        #     raise BadRequest(detail="bad request: `type` must be one of the following 1 | 2 | 3")
        
    def get_object(self):
        queryset = self.get_queryset()
        lookup_value = self.request.data.get("id")
        obj = get_object_or_404(queryset, **{self.lookup_field: lookup_value})
        return obj

    def perform_create(self, serializer):
        serializer.save()
