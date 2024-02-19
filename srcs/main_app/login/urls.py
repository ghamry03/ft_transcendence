from django.urls import path

from . import views

urlpatterns = [
    path('login/', views.loginPage, name='login'),
    path('logout/', views.logout, name='login'),
    path('authenticate/', views.authenticate, name='authenticate'),
    path('renew_token/', views.renew_token, name='renew_token'),
]
