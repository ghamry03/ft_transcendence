from django.urls import path

from .views import (
    UsersListApiView,
    UserDetailApiView,
	health_check
)

urlpatterns = [
    path('api/', UsersListApiView.as_view()),
    path('api/<int:user_id>/', UserDetailApiView.as_view()),
	path('health', health_check, name='health_check'),
]
