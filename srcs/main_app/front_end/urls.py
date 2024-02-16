from django.urls import path

from . import views

urlpatterns = [
    path('', views.index, name='index'),
    path('home/', views.homePage, name='home'),
    path('cards/', views.homeCards, name='home_cards'),
    path('topbar/', views.topBar, name='topBar'),
    # path('tournament/', views.tournament, name="tournament"),
    path('playerInfo/', views.getOpponentInfo, name='getOpponentInfo'),
]
