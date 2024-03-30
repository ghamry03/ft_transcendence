from django.urls import path

from .views import (
        views,
        login_views,
        game_views,
        home_views,
        profile_views,
        friends_views
)

urlpatterns = [
    # views
    path('api/session-data/', views.SessionDataView.as_view(), name='session-data'),
    path('playerInfo/', views.getOpponentInfo, name='getOpponentInfo'),

    # HOME
    path('', home_views.index, name='index'),
    path('home/', home_views.homePage, name='home'),
    path('topbar/', home_views.topBar, name='topBar'),
    path('cards/', home_views.homeCards, name='home_cards'),
    path('sideBar/', home_views.sideBar, name='sideBar'),
    path('sideBarMobile/', home_views.sideBarMobile, name='sideBarMobile'),

    # LOGIN
    path('login/', login_views.loginPage, name='login'),
    path('logout/', login_views.logout, name='login'),
    path('authenticate/', login_views.authenticate, name='authenticate'),
    path('renew_token/', login_views.renew_token, name='renew_token'),

    # PROFILE
    path('profile/<int:uid>/', profile_views.profile, name='profile'),
    path('status/<int:status>/', profile_views.updateStatus, name='status'),
    path('edit_profile/', profile_views.edit_profile, name='edit_profile'),

    # FRIENDS
    path('add/<friendUID>/', friends_views.addUser, name='addUsers'),
    path('accept/<friendUID>/', friends_views.acceptFriend, name='acceptUsers'),
    path('reject/<friendUID>/', friends_views.rejectFriend, name='removeUsers'),
    path('searchUsers/<username>/', friends_views.searchUsers, name='searchUsers'),

    # GAME
    path('online/', game_views.onlineGame, name="onlineGame"),
    path('offline/', game_views.offlineGame, name="offlineGame"),
    path('tournament/', game_views.tournament, name="tournament"),
    path('gameUrl/', game_views.getGameUrl, name="gameUrl"),
    path('tourUrl/', game_views.getTourUrl, name="tourUrl"),
]
