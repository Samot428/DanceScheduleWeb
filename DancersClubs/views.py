from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from TrainerClubs.models import Club
from main.models import Day, Couple, Trainer, Dancer
from django.core.paginator import Paginator
from django.http import JsonResponse
from django.contrib import messages
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

def find_club(request):
    """View of the specific clubs"""
    if request.method != 'POST':
        return JsonResponse({'error': 'Method not allowed'}, status=405)
    club_name = request.POST.get('looking_for_club')
    if club_name == 'all':
        clubs = Club.objects.all()
        return render(request, 'dancers_clubs_view.html', {'clubs':clubs})
    club = get_object_or_404(Club, name=club_name)
    return render(request, 'dancers_clubs_view.html', {'clubs': [club]})

def add_couple(request, club_id):
    """Add a couple to day by a dancer"""
    if request.method != 'POST':
        return JsonResponse({'error':'Method not allowed'}, status=405)

    day_id = request.POST.get('day_id')
    if day_id:
        confirmed = request.POST.get('confirmed') == 'true'
        club = get_object_or_404(Club, id=club_id)    
        day = get_object_or_404(Day, id=day_id, club=club)
        try:
            couple = get_object_or_404(Couple, uid=request.user.id)
            day.couples.add(couple)
            day.save()
        except:
            dancer = get_object_or_404(Dancer, uid=request.user.id)
            day.dancers.add(dancer)
            day.save()
        
    return redirect(f'/dancer/club/{club_id}')

def delete_couple(request, club_id):
    """Delete a couple from day by a dancer"""
    if request.method != 'POST':
        return JsonResponse({'error':'Method not allowed'}, status=405)

    club = get_object_or_404(Club, id=club_id)
    day_id = request.POST.get('day_id')
    day = get_object_or_404(Day, id=day_id, club=club)

    try:
        couple = get_object_or_404(Couple, id=request.user.id)
        # continue here with deleting the couple with its availability!!! almos there :)
    except:
        pass