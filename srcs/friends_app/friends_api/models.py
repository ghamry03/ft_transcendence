from django.db import models
from user_api.models import User

# Create your models here.

RELATIONSHIP_CHOICE = [
    (0, 'friend'),
    (1, 'pending')
]
class Friend(models.Model):
    id = models.BigAutoField(primary_key=True)
    first_user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='first_friends')
    second_user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='second_friends')
    first_id = models.BigIntegerField()
    second_id = models.BigIntegerField()
    relationship = models.SmallIntegerField(
        choices=RELATIONSHIP_CHOICE,
        default=1
    )

