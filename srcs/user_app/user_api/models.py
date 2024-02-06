from django.db import models
from .oauth_42 import oauth_42
from django.db.models.signals import pre_delete
from django.dispatch import receiver

# Create your models here.
class User(models.Model):
    uid = models.BigIntegerField(
            primary_key=True,
            unique=True,
    )
    username = models.CharField(
            max_length=64,
            unique=True,
    )
    first_name = models.CharField(
            max_length=64
    )
    image = models.ImageField(
        # upload_to=settings.MEDIA_ROOT
    )
    STATUS_CHOICE = [
        (0, 'Offline'),
        (1, 'Online'),
        (2, 'In Game'),
    ]
    status = models.SmallIntegerField(
        choices=STATUS_CHOICE,
        default=0,
    )

    def __str__(self):
        return f"""id: {self.uid} - username: {self.username} -
                picture: {self.image} - status: {self.status}
            """

    def oaut_42_user(self, token):
        api = oauth_42(token)
        api.get_user(self)

class TourGameTournament(models.Model):
    starttime = models.DateTimeField()
    endtime = models.DateTimeField()

    class Meta:
        managed = False
        db_table = 'tour_game_tournament'

class OnlineGame(models.Model):
    starttime = models.DateTimeField()
    endtime = models.DateTimeField()
    tournament = models.ForeignKey(TourGameTournament, models.CASCADE, blank=True, null=True)

    class Meta:
        managed = False
        db_table = 'online_game'

class OnlinePlayermatch(models.Model):
    score = models.IntegerField(blank=True, null=True)
    game = models.ForeignKey(OnlineGame, models.CASCADE, blank=True, null=True)
    player = models.ForeignKey(User, models.CASCADE, blank=True, null=True)

    class Meta:
        managed = False
        db_table = 'online_playermatch'
        
@receiver(pre_delete, sender=User)
def delete_related_player_match(sender, instance, **kwargs):
    playerMatches = OnlinePlayermatch.objects.filter(player=instance)
    gids = playerMatches.values_list('game_id', flat=True)
    OnlineGame.objects.filter(id__in=gids).delete()