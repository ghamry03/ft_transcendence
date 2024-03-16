from django.urls import path

from . import views

urlpatterns = [
    path('', views.index, name='index'),
    path('home/', views.homePage, name='home'),
    path('searchUsers/<username>/', views.searchUsers, name='searchUsers'),
    path('add/<friendUID>/', views.addUser, name='addUsers'),
    path('accept/<friendUID>/', views.acceptFriend, name='addUsers'),
    path('reject/<friendUID>/', views.rejectFriend, name='addUsers'),
    path('cards/', views.homeCards, name='home_cards'),
    path('topbar/', views.topBar, name='topBar'),
    path('playerInfo/', views.getOpponentInfo, name='getOpponentInfo'),
    path('api/session-data/', views.SessionDataView.as_view(), name='session-data'),
]
