from django.urls import path

from .views import (
	UserMatchListApiView,
	TournamentGameListApiView,
	MatchPlayerListApiView,
	health_check
)

urlpatterns = [
	path('matchHistory/<int:player>/', UserMatchListApiView.as_view()),
	path('tournamentsGames/<int:id>/', TournamentGameListApiView.as_view()),
	path('players/<int:gid>/', MatchPlayerListApiView.as_view()),
	path('health', health_check, name='health_check'),
]
