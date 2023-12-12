from django.urls import path
from .views import (
        UsersListApiView,
)

urlpatterns = [
    path('api/', UsersListApiView.as_view()),
]
