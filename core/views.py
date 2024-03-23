from django.shortcuts import render
from bot.views import keep_fetching


def home_view(request):
    keep_fetching()
    return render(request, 'home.html', {})
