from django.shortcuts import render
from .models import Club
from django.contrib.auth.decorators import login_required
# Create your views here.

@login_required
def dashboard(request):
    """Shows the trainer clubs"""
    
    clubs = Club.objects.filter(club_owner=request.user)

    return render(request, 'clubs_view.html', {'clubs':clubs})

@login_required
def add_club(request):
    """Adds club to the user"""
    if request.method == 'POST':
        name = request.POST.get('club_name')
        if name:  # Basic validation
            club = Club(name=name, club_owner=request.user)
            club.save()
            return redirect('dashboard')  # Redirect to dashboard after adding
    # For GET or invalid POST, show the dashboard
    clubs = Club.objects.filter(club_owner=request.user)
    return render(request, 'clubs_view.html', {'clubs': clubs})