from django.contrib import admin
from .models import TourGameTournament, Game, PlayerMatch

# Register your models here.

# admin.site.register(UserApiUser)
admin.site.register(TourGameTournament)
admin.site.register(Game)
admin.site.register(PlayerMatch)
