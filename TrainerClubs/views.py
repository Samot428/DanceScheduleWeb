from django.shortcuts import render, redirect, get_object_or_404
from .models import Club
from main.models import Day, Trainer, GroupLesson, TrainerDayAvailability, Group
from django.core.paginator import Paginator
from django.contrib.auth.decorators import login_required
from django.http import JsonResponse
from django.contrib import messages
from datetime import time
import json
# Create your views here.

@login_required
def dashboard(request):
    """Shows the trainer clubs"""
    
    clubs = Club.objects.all()

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
    clubs = Club.objects.all()
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

def show_not_trainer_club(request, club_id):
    """View of the club for non-club owner"""
    
    club = get_object_or_404(Club, id=club_id)
    days = Day.objects.filter(club=club).all()
    trainers = Trainer.objects.filter(club=club).all()
    paginator = Paginator(days, 2)
    page_number = request.GET.get('page',1)
    page_obj = paginator.get_page(page_number)

    return render(request, 'non_club_owner_view.html', {'club':club, 'days':page_obj.object_list, 'page_obj':page_obj, 'trainers': trainers})

def add_trainer_to_day(request, club_id):
    """The user can add him self as a trainer to this day"""
    if request.method != 'POST':
        return JsonResponse({'error':'Method not allowed'}, status=405)
    
    trainer_id = request.POST.get('trainer_id')
    day_id = request.POST.get('day_id')
    start_time = request.POST.get('start_time')
    end_time = request.POST.get('end_time')
    g = request.POST.get('groups')
    club = get_object_or_404(Club, id=club_id)
    if day_id and trainer_id:
        day = get_object_or_404(Day, id=day_id, club=club)
        trainer = get_object_or_404(Trainer, id=trainer_id, club=club)
        day.trainers.add(trainer)
        day.save

        avail, created = TrainerDayAvailability.objects.update_or_create(
            day=day,
            trainer=trainer,
            club=club,
            defaults = {
                'start_time': day.start_time,
                'end_time': day.end_time,
                'user': club.club_owner
            }
        )

        if start_time and end_time:
            try:
                sh, sm = map(int, start_time.split(":"))
                eh, em = map(int, end_time.split(":"))
                start_obj = time(sh, sm)
                end_obj = time(eh, em)
            except Exception:
                messages.warning(request, "Invalid time format for the group lesson.")
                return redirect(f'/trainer/club/trainer_view/<int:club_id>/')
            
            if start_obj >= end_obj:
                messages.warning(request, "Start_time must be before End_time.")
                return redirect(f'/trainer/club/trainer_view/<int:club_id>/')

            overlap = False
            can_be = True
            for lesson in trainer.group_lesson.filter(day=day):
                if (start_obj < lesson.time_interval_end) and (end_obj > lesson.time_interval_start):
                    overlap = True
                    break
                if (TrainerDayAvailability.objects.get(trainer=trainer, day=day).start_time > lesson.time_interval_start) or (TrainerDayAvailability.objects.get(trainer=trainer, day=day).end_time < lesson.time_interval_end) or (day.start_time > lesson.time_interval_start) or (day.end_time < lesson.time_interval_end):
                    can_be = False
                    break   
            try:
                if ',' in g:
                    aimed_groups = g.split(',')
                else:
                    aimed_groups = []
                    aimed_groups.append(g)
                ag = []
                for aim_group in aimed_groups:
                    ag.append(Group.objects.get(name=aim_group.strip(), user=club.club_owner))
            except Exception as e:
                ag = request.user.owned_groups.all()
            if overlap:
                    messages.warning(request, "This lesson overlaps an existing lesson for this trainer.")
            elif not can_be:
                messages.warning(request, "This lesson can't be scheduled because of the start time and end time of the lesson")
            else:
                grouplesson = GroupLesson(day=day, club_id=club_id, time_interval_start=start_obj, time_interval_end=end_obj, user=club.club_owner)
                grouplesson.save()
                for x in ag:
                    grouplesson.groups.add(x)
                trainer.group_lesson.add(grouplesson)
                trainer.save()
                messages.success(request, f"Trainer '{trainer.name}' with group lesson added successfully!")

            if not start_time or not end_time:
                messages.success(request, f"Trainer '{trainer.name}' added successfully!")
            
            return redirect(f'/trainer/club/trainer_view/{club.id}/')
    return redirect(f'/trainer/club/trainer_view/{club.id}/')      

def update_trainer_time(request, trainer_id, club_id):
    """Update a trainer's per-day start/end time via AJAX (JSON) by the user that is not a club owner.

    Expects JSON with:
      - day_id: int (required)
      - start_time: "HH:MM" (optional)
      - end_time: "HH:MM" (optional)

    Updates TrainerDayAvailability for (day, trainer). Creates one if missing,
    defaulting to the Day's start/end times. Supports partial updates.
    """
    if request.method != 'POST':
        return JsonResponse({'error': 'Method not allowed'}, status=405)
    club=get_object_or_404(Club, id=club_id)
    trainer = get_object_or_404(Trainer, id=trainer_id, club=club)
    try:
        payload = json.loads(request.body.decode('utf-8'))
    except json.JSONDecodeError:
        return JsonResponse({'error': 'Invalid JSON'}, status=400)

    day_id = payload.get('day_id')
    if not day_id:
        return JsonResponse({'error': 'day_id is required'}, status=400)
    day = get_object_or_404(Day, id=day_id, club=club)
    incoming_start = payload.get('start_time')
    incoming_end = payload.get('end_time')
    if incoming_start is None and incoming_end is None:
        return JsonResponse({'error': 'Provide start_time and/or end_time'}, status=400)

    # Get or create availability defaulting to day's bounds
    availability, created = TrainerDayAvailability.objects.get_or_create(
        day=day, trainer=trainer, club=club, user=club.club_owner,
        defaults={'start_time': day.start_time, 'end_time': day.end_time}
    )
    if created or availability.user != club.club_owner:
        availability.user = club.club_owner
        availability.save()
    
    # Parse provided times; use existing otherwise
    try:
        if incoming_start is not None:
            sh, sm = map(int, str(incoming_start).split(':'))
            new_start = time(sh, sm)
        else:
            new_start = availability.start_time
        if incoming_end is not None:
            eh, em = map(int, str(incoming_end).split(':'))
            new_end = time(eh, em)
        else:
            new_end = availability.end_time
    except Exception:
        print('Invalid time format')
        return JsonResponse({'error': 'Invalid time format'}, status=400)

    if new_start >= new_end:
        print('new_start>=_new_end')
        return JsonResponse({'error': 'Start time must be before end time'}, status=400)

    # Optional: enforce within day bounds
    if new_start < day.start_time or new_end > day.end_time:
        print('day_bouds')
        return JsonResponse({'error': 'Times must be within day bounds'}, status=400)

    availability.start_time = new_start
    availability.end_time = new_end
    availability.save()

    return JsonResponse({
        'trainer_id': trainer.id,
        'day_id': day.id,
        'club_id': club_id,
        'start_time': availability.start_time.strftime('%H:%M'),
        'end_time': availability.end_time.strftime('%H:%M'),
    })
