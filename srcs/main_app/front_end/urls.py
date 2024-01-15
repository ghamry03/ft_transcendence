from django.urls import path

from . import views

urlpatterns = [
    path('', views.index, name="index"),
    path('login/', views.login, name="login"),
    path('home/', views.homeLoggedIn, name="home"),
    path('game/', views.loadGamePage, name="game"),
]