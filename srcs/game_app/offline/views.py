from django.shortcuts import render
from .models import UserApUser, Tournament, Game, PlayerMatch

# Create your views here.

def index(request):
    """View function for home page of site."""

    # Generate counts of some of the main objects
    num_users = UserApiUser.objects.all().count()
    num_tournaments = Tournament.objects.all().count()

    # Available users (status = 'a')
    num_tournaments_available = Tournament.objects.filter(tid__exact=1).count()

    # The 'all()' is implied by default.
    num_games = Game.objects.count()

    context = {
        'num_users': num_users,
        'num_tournaments': num_tournaments,
        'num_tournaments_available': num_tournaments_available,
        'num_games': num_games,
    }

    # Render the HTML template index.html with the data in the context variable
    return render(request, 'index.html', context=context)
