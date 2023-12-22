from django.db import models
from django.urls import reverse # Used to generate URLs by reversing the URL patterns

# GID, start time, end time 
class Game(models.Model):
	gid = models.AutoField(primary_key=True)
	def __str__(self):
        """String for representing the Model object."""
        return self.gid

    def get_absolute_url(self):
        """Returns the url to access a particular genre instance."""
        return reverse('game-detail', args=[str(self.gid)])