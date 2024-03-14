from django.urls import path

from . import views

urlpatterns = [
    path('', views.index, name='index'),
    path('home/', views.homePage, name='home'),
    path('searchUsers/<username>/', views.getUsers, name='getUsers'),
    path('cards/', views.homeCards, name='home_cards'),
    path('topbar/', views.topBar, name='topBar'),
    path('playerInfo/', views.getOpponentInfo, name='getOpponentInfo'),
]
