from django.db import models
from django.urls import reverse # Used to generate URLs by reversing the URL patterns

class UserApiUser(models.Model):
    id = models.BigIntegerField(primary_key=True)
    username = models.CharField(unique=True, max_length=64)
    first_name = models.CharField(max_length=64)
    last_name = models.CharField(max_length=64)

    class Meta:
        managed = False
        db_table = 'user_api_user'

class Tournament(models.Model):
    tid = models.AutoField(primary_key=True)
    startTime = models.DateField(auto_now_add=True)

class Game(models.Model):
    gid = models.AutoField(primary_key=True)
    startTime = models.DateField(auto_now_add=True)
    endTime = models.DateField(auto_now=True)
    tid = models.ForeignKey(Tournament, on_delete=models.CASCADE, null=True)
    def __str__(self):
        """String for representing the Model object."""
        return self.gid

    def get_absolute_url(self):
        """Returns the url to access a particular game instance."""
        return reverse('game-detail', args=[str(self.gid)])

class PlayerMatch(models.Model):
    matchId = models.AutoField(primary_key=True)
    gid = models.ForeignKey(Game, on_delete=models.CASCADE, null=True)
    pid = models.ForeignKey(UserApiUser, on_delete=models.CASCADE, null=True) # on deletion of the referenced object, this value will be set to null 
    score = models.IntegerField(null=True)
    def __str__(self):
        """String for representing the Model object."""
        return self.matchId

    def get_absolute_url(self):
        """Returns the url to access a particular genre instance."""
        return reverse('game-detail', args=[str(self.matchId)])
    