from django.db import models

class Tournament(models.Model):
    id = models.AutoField(primary_key=True)
    starttime = models.DateTimeField(auto_now_add=True)
    endtime = models.DateTimeField(auto_now_add=True)
