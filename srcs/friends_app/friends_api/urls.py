from django.urls import path
from rest_framework.urlpatterns import format_suffix_patterns
from friends_api import views
from .views import FriendDetailView

urlpatterns = [
    path('friends/', FriendDetailView.as_view(), name='friend-detail'),

]

urlpatterns = format_suffix_patterns(urlpatterns)