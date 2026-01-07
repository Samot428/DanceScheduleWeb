from django.shortcuts import render, redirect, get_object_or_404
from .models import Club
from django.contrib.auth.decorators import login_required
from django.http import JsonResponse
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
        profile_picture = request.FILES.get('profile_picture')
        if name:  # Basic validation
            club = Club(name=name, club_owner=request.user, profile_picture=profile_picture)
            club.save()
            return redirect('dashboard')  # Redirect to dashboard after adding
    # For GET or invalid POST, show the dashboard
    clubs = Club.objects.filter(club_owner=request.user)
    return render(request, 'clubs_view.html', {'clubs': clubs})

@login_required
def delete_club(request, club_id):
    """Deletes the club from the database"""
    if request.method != 'POST':
        return JsonResponse({'error':'Method not allowed'}, status=405)
    
    club = get_object_or_404(Club, id=club_id, club_owner=request.user)

    club.delete()
    return redirect('dashboard')

def update_club(request, club_id):
    """Updates Club info"""
    if request.method != 'POST':
        return JsonResponse({'error':'Method not allowed'}, status=405)

    name = request.POST.get('club_name')
    profile_picture = request.FILES.get('profile_picture')

    club = get_object_or_404(Club, id=club_id, club_owner=request.user)
    if name:
        club.name = name
    if profile_picture:
        club.profile_picture = profile_picture
    
    club.save()
    return redirect('dashboard')

@login_required
def show_club(request, club_id):
    """View of the seperate clubs"""
    club = get_object_or_404(Club, id=club_id, club_owner=request.user)
    # Redirect to the calendar view
    return redirect('calendar_view')


