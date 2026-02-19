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
    user_dancer = get_object_or_404(Dancer, uid=request.user.id)
    # Redirect to the calendar view
    return render(request, 'dancers_clubs_day_view.html', {'club':club, 'days':page_obj.object_list, 'page_obj':page_obj, 'user_dancer': user_dancer})

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

def delete_couple(request, club_id, couple_id):
    """Delete a couple from day by a dancer"""
    if request.method != 'POST':
        return JsonResponse({'error':'Method not allowed'}, status=405)

    club = get_object_or_404(Club, id=club_id)
    day_id = request.POST.get('day_id')
    day = get_object_or_404(Day, id=day_id, club=club)

    try:
        couple = Couple.objects.get(uid=couple_id)
        day.couples.remove(couple)
        day.save()
    except:
        dancer = Dancer.objects.get(uid=couple_id)
        day.dancers.remove(dancer)
        day.save()

    return redirect(f"/dancer/club/{club_id}")

def create_couple_view(request):
    """User can create a couple with another user (only one couple per user)"""

    dancer1 = get_object_or_404(Dancer, uid=request.user.id)
    clubs = Club.objects.all()
    dancers = Dancer.objects.filter(in_couple=False)

    return render(request, "dancers_create_couple_view.html", {'dancer1':dancer1, 'clubs':clubs, 'dancers':dancers})

def create_couple_by_user(request):
    if request.method != 'POST':
        return JsonResponse({'error':'Method not allowed'}, status=405)

    dancer1_id = request.POST.get('dancer1')
    dancer2_id = request.POST.get('dancer2')
    couple_class_stt = request.POST.get('classSTT')
    couple_class_lat = request.POST.get('classLAT')
    club_id = request.POST.get('club')
    
    dancer1 = get_object_or_404(Dancer, id=dancer1_id)
    dancer2 = get_object_or_404(Dancer, id=dancer2_id)
    club = get_object_or_404(Club, id=club_id)
    
    return redirect('/dancer/create_view/')