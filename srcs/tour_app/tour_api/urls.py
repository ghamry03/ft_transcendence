from django.urls import path


from .views import (
	TournamentHistoryApiView,
	TournamentMatchesApiView,
	health_check
)

urlpatterns = [
	path('tourhistory/<int:user_id>/', TournamentHistoryApiView.as_view()),
	path('tourmatches/<int:t_id>/', TournamentMatchesApiView.as_view()),
	path('health', health_check, name='health_check'),
]