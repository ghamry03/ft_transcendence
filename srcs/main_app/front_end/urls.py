from django.urls import path

from . import views

urlpatterns = [
    path('', views.index, name='index'),
    path('home/', views.homeLoggedIn, name='home'),
    path('login/', views.loginPage, name='login'),
    path('topbar/', views.topBar, name='topBar'),
    path('token/', views.token, name='token'),
    path('renew_token/', views.renew_token, name='renew_token')
]
