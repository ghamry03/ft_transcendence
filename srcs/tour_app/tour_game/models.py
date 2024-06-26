from django.db import models
from django.db.models.signals import pre_delete
from django.dispatch import receiver
from django.utils import timezone

class UserApiUser(models.Model):
    uid = models.BigIntegerField(primary_key=True, unique=True)
    username = models.CharField(max_length=64, unique=True)
    first_name = models.CharField(max_length=64)
    last_name = models.CharField(max_length=64)
    campus_name = models.CharField(max_length=64)
    intra_url = models.CharField(max_length=64)
    image = models.ImageField()
    status = models.SmallIntegerField()

    class Meta:
        managed = False
        db_table = 'user_api_user'

class Tournament(models.Model):
    id = models.AutoField(primary_key=True)
    starttime = models.DateTimeField(auto_now_add=True)
    endtime = models.DateTimeField(auto_now_add=True)

class TournamentRank(models.Model):
    id = models.AutoField(primary_key=True)
    player = models.ForeignKey(UserApiUser, models.CASCADE, blank=True, null=True)
    rank = models.IntegerField()
    tournament = models.ForeignKey(Tournament, models.CASCADE, blank=True, null=True)

class OnlineGame(models.Model):
    starttime = models.DateTimeField()
    endtime = models.DateTimeField()
    tournament = models.ForeignKey(Tournament, models.CASCADE, blank=True, null=True)

    class Meta:
        managed = False
        db_table = 'online_game'

class OnlinePlayermatch(models.Model):
    score = models.IntegerField(blank=True, null=True)
    game = models.ForeignKey(OnlineGame, models.CASCADE, blank=True, null=True)
    player = models.ForeignKey(UserApiUser, models.CASCADE, blank=True, null=True)

    class Meta:
        managed = False
        db_table = 'online_playermatch'
