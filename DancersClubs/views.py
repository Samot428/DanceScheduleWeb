from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from TrainerClubs.models import Club
from main.models import Day, Couple, Trainer
from django.core.paginator import Paginator
# Create your views here.
@login_required
def dancers_dashboard(request):
    """Shows the trainer clubs"""
    
    clubs = Club.objects.all()
    return render(request, 'dancers_clubs_view.html', {'clubs':clubs})

@login_required
def show_club(request, club_id):
    """View of the seperate clubs"""
    club = get_object_or_404(Club, id=club_id)
    days = Day.objects.filter(club=club).all()
    paginator = Paginator(days, 2)
    page_number = request.GET.get('page',1)
    page_obj = paginator.get_page(page_number)
    # Redirect to the calendar view
    return render(request, 'dancers_clubs_day_view.html', {'club':club, 'days':page_obj.object_list, 'page_obj':page_obj})