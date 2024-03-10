from django.urls import path

from .views import (
	TournamentGameListApiView,
	MatchPlayerListApiView,
	MatchHistoryApiView,
	CreateGameApiView,
	EndGameApiView,
	health_check
)

urlpatterns = [
	path('matchhistory/<int:user_id>/', MatchHistoryApiView.as_view()),
	path('tournamentsgames/<int:id>/', TournamentGameListApiView.as_view()),
	path('players/<int:gid>/', MatchPlayerListApiView.as_view()),
	path('createGame/<int:pid1>/<int:pid2>/<int:tid>/', CreateGameApiView.as_view()),
	path('endGame/<int:gid>/<int:pid1>/<int:pid2>/<int:score1>/<int:score2>/', EndGameApiView.as_view()),
	path('health', health_check, name='health_check'),
]