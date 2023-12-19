from django.db import models

# Create your models here.
class User(models.Model):
    id = models.BigAutoField(
            primary_key=True,
            unique=True,
    )
    username = models.CharField(
            max_length=64,
            unique=True,
    )
    first_name = models.CharField(
            max_length=64,
    )
    last_name = models.CharField(
            max_length=64,
    )

    def __str__(self):
        return f"""id: {self.id} - username: {self.username} -
                firstName: {self.first_name} - lastName: {self.last_name}
            """
