from django.urls import path

from .views import (
    UsersListApiView,
    UserDetailApiView,
    UserSearch,
    health_check
)

urlpatterns = [
    path('users/', UsersListApiView.as_view()),
    path('user/<int:user_id>/', UserDetailApiView.as_view()),
    path('search/<str:pattern>/', UserSearch.as_view()),
    path('health', health_check, name='health_check'),
]
