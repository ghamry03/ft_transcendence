# from django.db import models
# from user_api.models import User

# # Create your models here.

# RELATIONSHIP_CHOICE = [
#     (0, 'friend'),
#     (1, 'pending')
# ]
# class Friend(models.Model):
#     id = models.BigAutoField(
#             primary_key=True,
#             unique=True,
#     )

#     first_id = models.ForeignKey(
#         User,
#         on_delete=models.CASCADE,
#         related_name='first_friends',
#         db_constraint=False)
    
#     second_id = models.ForeignKey(
#         User,
#         on_delete=models.CASCADE,
#         related_name='second_friends',
#         db_constraint=False)
    
#     relationship = models.SmallIntegerField(
#         choices=RELATIONSHIP_CHOICE,
#         default=1
#     )

from django.db import models
from user_api.models import User

# Create your models here.

RELATIONSHIP_CHOICE = [
    (0, 'friend'),
    (1, 'pending')
]
class Friend(models.Model):
    id = models.BigAutoField(
            primary_key=True,
            unique=True,
    )

    first_id = models.BigIntegerField()
    
    second_id = models.BigIntegerField()
    
    relationship = models.SmallIntegerField(
        choices=RELATIONSHIP_CHOICE,
        default=1
    )

