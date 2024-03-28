from django.shortcuts import render
from django.contrib.auth.decorators import login_required
from django.contrib.auth import logout


def home_view(request):
    # keep_fetching()
    return render(request, 'home.html', {})


@login_required
def profile_view(request):
    user = request.user
    if not user.is_authenticated:
        return render(request, 'home.html', {})
    return render(request, 'registration/profile.html', {'user':user})


@login_required
def logout_view(request):
    if request.method == 'POST':
        logout(request)
        return render(request, 'registration/logout.html', {})
    