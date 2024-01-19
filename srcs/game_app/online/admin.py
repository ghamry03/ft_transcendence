from django.contrib import admin
from .models import Tournament, Game, PlayerMatch

# Register your models here.

# admin.site.register(UserApiUser)
admin.site.register(Tournament)
admin.site.register(Game)
admin.site.register(PlayerMatch)
