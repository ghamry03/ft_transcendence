from django.db import models

class Tournament(models.Model):
    id = models.AutoField(primary_key=True)
    starttime = models.DateTimeField(auto_now_add=True)
    endtime = models.DateTimeField(auto_now_add=True)

#create tournament instance
# tournament = Tournament()
# tournament.save()

class TournamentRank(models.Model):
    id = models.AutoField(primary_key=True)
    playerID = models.BigIntegerField()
    rank = models.IntegerField()
    tournament = models.ForeignKey(Tournament, models.DO_NOTHING, blank=True, null=True)

# create tournament rank instance
# tournament_rank = TournamentRank(playerID=1, rank=1, tournament=tournament)
# tournament_rank.save()

class UserApiUser(models.Model):
    uid = models.BigIntegerField(primary_key=True)
    username = models.CharField(unique=True, max_length=64)
    first_name = models.CharField(max_length=64)
    image = models.CharField(max_length=100)
    status = models.SmallIntegerField()
    class Meta:
        managed = False
        db_table = 'user_api_users'

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

# create playermatch instance
# playermatch = OnlinePlayermatch(score=100, game=game, player=1)
# playermatch.save()

# create game instance

t_instance = Tournament(starttime='2069-08-01 00:00:00', endtime='2069-08-01 10:10:10')
t_instance.save()

game2 = OnlineGame(starttime='2069-08-01 00:00:00', endtime='2069-08-01 10:10:10', tournament=t_instance)
game2.save()