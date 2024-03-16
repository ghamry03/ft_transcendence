from django.db import models
from django.urls import reverse # Used to generate URLs by reversing the URL patterns
from rest_framework import serializers
from django.db.models.signals import pre_delete
from django.dispatch import receiver

class UserApiUser(models.Model):
    uid = models.BigIntegerField(primary_key=True)
    username = models.CharField(unique=True, max_length=64)
    first_name = models.CharField(max_length=64)
    image = models.CharField(max_length=100)
    status = models.SmallIntegerField()

    class Meta:
        managed = False
        db_table = 'user_api_user'

class TourGameTournament(models.Model):
    starttime = models.DateTimeField()
    endtime = models.DateTimeField()

    class Meta:
        managed = False
        db_table = 'tour_game_tournament'

# this model stores game info that relates to the game overall and not one specific player
class Game(models.Model):
    id = models.AutoField(primary_key=True)
    starttime = models.DateTimeField(auto_now_add=True)
    endtime = models.DateTimeField(auto_now=True)
    tournament = models.ForeignKey(TourGameTournament, on_delete=models.CASCADE, null=True)
    def __str__(self):
        """String for representing the Model object."""
        return str(self.id)

    def get_absolute_url(self):
        """Returns the url to access a particular game instance."""
        return reverse('game-detail', args=[str(self.id)])

# this model stores info pertaining to one player in the game and their score
# we chose to separate PlayerMatch from Game to make fetching the data easier for one player 
class PlayerMatch(models.Model):
    id = models.AutoField(primary_key=True)
    game = models.ForeignKey(Game, on_delete=models.CASCADE, null=True)
    player = models.ForeignKey(UserApiUser, on_delete=models.CASCADE, null=True) # on deletion of the referenced object, this value will be set to null 
    score = models.IntegerField(null=True)
    def __str__(self):
        """String for representing the Model object."""
        return str(self.id)

    def get_absolute_url(self):
        """Returns the url to access a particular genre instance."""
        return reverse('game-detail', args=[str(self.id)])
