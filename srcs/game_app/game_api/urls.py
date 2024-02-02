from django.urls import path

from .views import (
	UserMatchListApiView,
	TournamentGameListApiView,
	MatchPlayerListApiView,
	MatchHistoryApiView,
	health_check
)

urlpatterns = [
	path('matchhistory/<int:user_id>/', MatchHistoryApiView.as_view()),
	path('tournamentsgames/<int:id>/', TournamentGameListApiView.as_view()),
	path('players/<int:gid>/', MatchPlayerListApiView.as_view()),
	path('health', health_check, name='health_check'),
]