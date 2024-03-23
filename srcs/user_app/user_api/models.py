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
from user_app.constants import FRIEND_API_URL

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

        headers = { 'Content-Type': 'application/json' }

        myuid = self.uid

        response = requests.delete(
            FRIEND_API_URL + "api/friends/",
            headers=headers,
            json={
                "first_user": f'{myuid}',
                "clean": 1, 
                },
        ).json()
        remove(self.image.path)
        return super(User, self).delete(*args, **kwargs)

#42 User
class FtUser(User):
    class Meta:
        proxy = True

    def __init__(self, *args, **kwargs):
        access_token = kwargs.pop('access_token', None)
        super().__init__(*args, **kwargs)
        if not self.uid and access_token:
            self._initialize_from_42(access_token)

    def _make_api_request(self, endpoint, access_token):
        headers = {'Authorization': f'Bearer {access_token}'}
        response = requests.get(f'https://api.intra.42.fr/v2/{endpoint}', headers=headers)
        if response.status_code != 200:
            raise exceptions.AuthenticationFailed('Failed to retrieve data from 42API')
        return response.json()

    def _update_existing_user_username(self, existing_user, access_token):
        updated_user_info = self._make_api_request(f'users/{existing_user.uid}', access_token)
        existing_user.username = updated_user_info['login']
        existing_user.save()

    def _initialize_from_42(self, access_token):
        user_data = self._make_api_request('me', access_token)

        existing_user = User.objects.filter(username=user_data['login']).first()
        if existing_user:
            self._update_existing_user_username(existing_user, access_token)

        self.uid = user_data.get('id')
        self.username = user_data.get('login')
        self.first_name = user_data.get('first_name')
        self.last_name = user_data.get('last_name')
        self.campus_name = user_data['campus'][0].get('name') if user_data.get('campus') else None
        self.intra_url = f'https://profile.intra.42.fr/users/{self.username}'

        self._save_profile_image(user_data.get('image', {}).get('link'), access_token)

        self.save()

    def _save_profile_image(self, image_url, access_token):
            if not image_url:
                image_path = settings.MEDIA_ROOT + 'johndoe.png'
                with open(image_path, 'rb') as default_image_file:
                    image_content = default_image_file.read()
            else:
                response = requests.get(image_url, headers={'Authorization': f'Bearer {access_token}'})
                image_content = response.content if response.status_code == 200 else None

                if not image_content:
                    image_path = settings.MEDIA_ROOT + 'johndoe.png'
                    with open(image_path, 'rb') as default_image_file:
                        image_content = default_image_file.read()

            with NamedTemporaryFile(delete=True) as temp_image_file:
                temp_image_file.write(image_content)
                temp_image_file.flush()
                filename = urlparse(image_url).path.split('/')[-1] if image_url else 'johndoe.png'
                self.image.save(filename, File(temp_image_file), save=True)


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
