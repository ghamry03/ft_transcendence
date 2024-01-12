from django.db import models
from .oauth_42 import oauth_42

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
