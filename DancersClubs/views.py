from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from TrainerClubs.models import Club
from main.models import Day, Couple, Trainer
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

    couple_name = request.POST.get('couple_name')
    min_duration = request.POST.get('min_duration')
    dance_class_stt = request.POST.get('dance_class_stt')
    dance_class_lat = request.POST.get('dance_class_lat')
    day_id = request.POST.get('day_id')
    club = get_object_or_404(Club, id=club_id)
    confirmed = request.POST.get('confirmed') == 'true'
    if not min_duration or min_duration.strip() == '':
        min_duration = 60
    else:
        int(min_duration)
    
    if day_id:
        day = get_object_or_404(Day, id=day_id, club=club)

        try:
            existing_couple = Couple.objects.get(name=couple_name)

            if day.couples.filter(id=existing_couple.id).exists():
                messages.warning(request, f"Couple '{couple_name}' is already in day '{day.name}'!")
                return redirect(f'/dancer/club/{club_id}')
            
            day.couples.add(existing_couple)
            messages.success(request, f"Couple '{couple_name}' added to day '{day.name}'!")
            return redirect(f'/dancer/club/{club_id}')

        except Couple.DoesNotExist:
            if not confirmed:
                messages.warning(request, f"Couple '{couple_name}' does not exist!")
                return redirect(f'/dancer/club/{club_id}')
            
            if not dance_class_stt or not dance_class_lat:
                messages.warning(request, f"Please provide bot Class STT and Class LAT for new couple '{couple_name}'!")
                return redirect(f'/dancer/club/{club_id}')
    return redirect(f'/dancer/club/{club_id}')
