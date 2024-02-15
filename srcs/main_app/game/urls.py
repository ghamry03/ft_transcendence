from django.urls import path

from . import views

urlpatterns = [
    path('online/', views.onlineGame, name="onlineGame"),
    path('offline/', views.offlineGame, name="offlineGame"),
]
