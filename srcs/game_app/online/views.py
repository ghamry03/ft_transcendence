from django.shortcuts import render
from .models import UserApiUser, Tournament, Game, PlayerMatch
import requests

def index(request):
    num_users = UserApiUser.objects.all().count()
    num_tournaments = Tournament.objects.all().count()

    # Available users (status = 'a')
    num_tournaments_available = Tournament.objects.filter(id__exact=1).count()

    # The 'all()' is implied by default.
    num_games = Game.objects.count()

    context = {
        'num_users': num_users,
        'num_tournaments': num_tournaments,
        'num_tournaments_available': num_tournaments_available,
        'num_games': num_games,
    }
    return render(request, "game.html", context=context)
