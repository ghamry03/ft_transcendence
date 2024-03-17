from django.urls import path

from . import views

urlpatterns = [
    path('', views.index, name='index'),
    path('home/', views.homePage, name='home'),
    path('cards/', views.homeCards, name='home_cards'),
    path('topbar/', views.topBar, name='topBar'),
    path('playerInfo/', views.getOpponentInfo, name='getOpponentInfo'),
    path('profile/<int:uid>/', views.profile, name='profile'),
    path('status/<int:status>/', views.updateStatus, name='status'),
    path('edit_profile/', views.edit_profile, name='edit_profile')
    path('unknownUserImg/', views.getUnknownUserImg, name='getUnknownUserImg'),
]
