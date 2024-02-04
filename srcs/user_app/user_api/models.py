from django.db import models
from .oauth_42 import oauth_42
from os import remove

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
    image = models.ImageField()
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

    def new_42_user(self, token):
        api = oauth_42(token)
        api.create_user(self)
        self.save()
