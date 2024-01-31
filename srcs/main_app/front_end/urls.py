from django.urls import path

from . import views

urlpatterns = [
    path('', views.index, name="index"),
    path('login/', views.login, name="login"),
    path('home/', views.homeLoggedIn, name="home"),
    path('online/', views.onlineGame, name="onlineGame"),
    path('offline/', views.offlineGame, name="offlineGame"),
    path('tournament/', views.tournament, name="tournament"),
	path('playerInfo/', views.getOpponentInfo, name='getOpponentInfo'),
	
]