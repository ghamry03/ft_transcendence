from django.db import models

class Tournament(models.Model):
    id = models.AutoField(primary_key=True)
    starttime = models.DateTimeField(auto_now_add=True)
    endtime = models.DateTimeField(auto_now_add=True)
    ranks = models.ArrayField(
        models.BigIntegerField(blank=True, null=True),
        size=8,
        default=[None]*8
    )
class UserApiUser(models.Model):
    uid = models.BigIntegerField(primary_key=True)
    username = models.CharField(unique=True, max_length=64)
    first_name = models.CharField(max_length=64)
    image = models.CharField(max_length=100)
    status = models.SmallIntegerField()

    class Meta:
        managed = False
        db_table = 'user_api_user'

class OnlineGame(models.Model):
    starttime = models.DateTimeField()
    endtime = models.DateTimeField()
    tournament = models.ForeignKey(Tournament, models.DO_NOTHING, blank=True, null=True)


    class Meta:
        managed = False
        db_table = 'online_game'


class OnlinePlayermatch(models.Model):
    score = models.IntegerField(blank=True, null=True)
    game = models.ForeignKey(OnlineGame, models.DO_NOTHING, blank=True, null=True)
    player = models.ForeignKey(UserApiUser, models.DO_NOTHING, blank=True, null=True)

    class Meta:
        managed = False
        db_table = 'online_playermatch'