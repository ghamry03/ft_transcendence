from django.urls import path
from .views import (
        UsersListApiView,
        UserDetailApiView,
)

urlpatterns = [
    path('api/', UsersListApiView.as_view()),
    path('api/<int:user_id>/', UserDetailApiView.as_view()),
]
