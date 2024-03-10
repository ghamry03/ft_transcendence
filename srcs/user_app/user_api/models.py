from django.db import models
from os import remove
from django.db.models.signals import pre_delete
from django.dispatch import receiver
import requests
from rest_framework import exceptions
from django.core.files.temp import NamedTemporaryFile
from urllib.parse import urlparse
from django.core.files import File
from django.conf import settings

# Create your models here.
class User(models.Model):
    uid = models.BigIntegerField(primary_key=True, unique=True)
    username = models.CharField(max_length=64, unique=True)
    first_name = models.CharField(max_length=64)
    last_name = models.CharField(max_length=64)
    campus_name = models.CharField(max_length=64)
    intra_url = models.CharField(max_length=64)
    image = models.ImageField()
    STATUS_CHOICE = [(0, 'Offline'),(1, 'Online'),(2, 'In Game'),]
    status = models.SmallIntegerField(choices=STATUS_CHOICE,default=0)

    def __str__(self):
        return f"""id: {self.uid} - username: {self.username} -
                    first_name: {self.first_name} -
                    picture: {self.image} - status: {self.status}
            """

    def save(self, *args, **kwargs):
        try:
            this = User.objects.get(uid=self.uid)
            if this.image != self.image :
                remove(this.image.path)
        except: pass
        super(User, self).save(*args, **kwargs)

    def delete(self, *args, **kwargs):
        remove(self.image.path)
        return super(User, self).delete(*args, **kwargs)

#42 User
class ft_user(User):
    class Meta:
        proxy = True

    def __init__(self, *args, **kwargs):
        access_token = kwargs.pop('access_token', None)
        super().__init__(*args, **kwargs)
        if not self.uid and access_token:
            self.retrieve_from_42(access_token)

    def retrieve_from_42(self, access_token):
        url = 'https://api.intra.42.fr/v2/me'
        headers = { 'Authorization': 'Bearer ' + access_token }
        response = requests.get(url, headers=headers)
        if response.status_code != 200:
            raise exceptions.AuthenticationFailed('Failed to connect to intra')
        json_data = response.json()

        self.uid = int(json_data['id'])
        self.username = json_data['login']
        self.first_name = json_data['first_name']
        self.last_name = json_data['last_name']
        self.campus_name = json_data['campus'][0]['name']
        self.intra_url = f'https://profile.intra.42.fr/users/{json_data["login"]}'

        image_url = json_data['image']['link']
        image_response = requests.get(image_url)
        content = ""
        if image_response.status_code != 200:
            imgFile = open(settings.MEDIA_ROOT + 'johndoe.png', 'rb')
            content = imgFile.read()
            imgFile.close()
        else:
            content = image_response.content
        img_temp = NamedTemporaryFile(delete=True)
        img_temp.write(content)
        img_temp.flush()

        self.image.save(
            urlparse(image_url).path.split('/')[-1],
            File(img_temp),
            save=True
        )

class OnlineTournament(models.Model):
    starttime = models.DateTimeField()
    endtime = models.DateTimeField()

    class Meta:
        managed = False
        db_table = 'online_tournament'

class OnlineGame(models.Model):
    starttime = models.DateTimeField()
    endtime = models.DateTimeField()
    tournament = models.ForeignKey(OnlineTournament, models.CASCADE, blank=True, null=True)

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
