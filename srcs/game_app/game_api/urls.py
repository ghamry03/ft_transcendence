from django.urls import path

from .views import (
	UserMatchListApiView,
	TournamentGameListApiView,
	MatchPlayerListApiView,
	health_check
)

urlpatterns = [
	path('api/<int:player>/', UserMatchListApiView.as_view()),
	path('api/<int:id>/', TournamentGameListApiView.as_view()),
	path('api/<int:gid>/', MatchPlayerListApiView.as_view()),
	path('health', health_check, name='health_check'),
]
