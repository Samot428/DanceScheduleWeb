from django.shortcuts import render, redirect, get_object_or_404
from django.http import HttpResponse
from django.contrib import messages
from .models import Couple, Trainer, Group, Day, GroupLesson, TrainerDayAvailability
from .models import TrainerDayAvailability
from datetime import time
from django.core.paginator import Paginator
from django.http import JsonResponse
import json
from django.template.loader import render_to_string
from django.views.decorators.http import require_GET, require_POST
from django.contrib.auth.forms import UserCreationForm, AuthenticationForm
from django.contrib.auth import login, logout
from django.contrib.auth.decorators import login_required
from django.views.decorators.csrf import csrf_exempt
from .forms import CustomUserCreationForm
from .models import UserProfile

def custom_login(request):
    """Custom login view that redirects based on user type"""
    if request.method == 'POST':
        form = AuthenticationForm(request, data=request.POST)
        if form.is_valid():
            user = form.get_user()
            login(request, user)
            # Redirect based on user type
            try:
                user_profile = user.userprofile
                if user_profile.user_type == 'trainer':
                    return redirect('dashboard')  # Redirect to TrainerClubs dashboard
                else:  # dancer
                    return redirect('home')
            except UserProfile.DoesNotExist:
                return redirect('home')  # Default if no profile
    else:
        form = AuthenticationForm()
    return render(request, 'registration/login.html', {'form': form})


from .models import UserProfile

def signup(request):
    """The user can sign up into the site"""
    if request.method == 'POST':
        form = CustomUserCreationForm(request.POST)
        if form.is_valid():
            user = form.save()
            user_type = form.cleaned_data['user_type']
            UserProfile.objects.create(user=user, user_type=user_type)
            login(request, user)
            # Redirect based on user type
            if user_type == 'trainer':
                return redirect('dashboard')  # Redirect to TrainerClubs dashboard
            else:  # dancer
                return redirect('home')
    else:
        form = CustomUserCreationForm()
    return render(request, "registration/signup.html", {'form': form})

def custom_logout(request):
    """Custom logout view that logs out the user and redirects to login page"""
    logout(request)
    return redirect('login')

# @login_required
# def trainer_dashboard(request):
#     """Dashboard for trainers"""
#     # For now, just show the same as home, but you can customize
#     trainers = request.user.trainer.all()
#     groups = request.user.owned_groups.all()
#     days = request.user.day.all()
#     return render(request, 'calendar_view.html', {'groups': groups, 'trainers': trainers, 'days': days})

@login_required
def couples_groups(request):
    """Display the couples and groups page"""
    trainers = request.user.trainer.all() # get all trainers from database
    groups = request.user.owned_groups.all()
    days = request.user.day.all()

    # Pass data to template
    return render(request, 'calendar_view.html', {'groups':groups, 'trainers':trainers, 'days':days})

# Couples

@login_required
def add_couple(request):
    """Add a new couple to the database """
    if request.method == 'POST':
        # Get the data from the form
        couple_name = request.POST.get('couple_name')
        min_duration = request.POST.get('min_duration')
        dance_class_stt = request.POST.get('dance_class_stt')
        dance_class_lat = request.POST.get('dance_class_lat')
        group_id = request.POST.get('group_id')
        day_id = request.POST.get('day_id')
        confirmed = request.POST.get('confirmed') == 'true'
        
        # If min_duration is empty or not provided, use default (60)
        if not min_duration or min_duration.strip() == '':
            min_duration = 60
        else:
            min_duration = int(min_duration)
        
        # Determine where to redirect back to
        referer = request.META.get('HTTP_REFERER', '')
        redirect_to_manage = 'manage_groups' in referer
        page = request.POST.get('page')
        
        # Special handling when adding to a day
        if day_id:
            day = get_object_or_404(Day, id=day_id, user=request.user)
            
            # Try to find existing couple
            try:
                existing_couple = Couple.objects.get(name=couple_name, user=request.user)
                
                # Check if couple already in this day
                if day.couples.filter(id=existing_couple.id).exists():
                    messages.warning(request, f'Couple "{couple_name}" is already in day "{day.name}"!')
                    if 'manage_days' in referer:
                        if page:
                            return redirect(f"/manage_days/?page={page}")
                        return redirect('manage_days')
                    return redirect('calendar_view')
                
                # Couple exists but not in this day - add it automatically
                day.couples.add(existing_couple)
                messages.success(request, f'Couple "{couple_name}" added to day "{day.name}"!')
                if 'manage_days' in referer:
                    if page:
                        return redirect(f"/manage_days/?page={page}")
                    return redirect('manage_days')
                return redirect('calendar_view')
                
            except Couple.DoesNotExist:
                # Couple doesn't exist - needs confirmation (handled by frontend)
                # If not confirmed, this shouldn't happen (frontend handles it)
                # But if confirmed=true, proceed to create
                if not confirmed:
                    messages.warning(request, f'Couple "{couple_name}" does not exist!')
                    if 'manage_days' in referer:
                        if page:
                            return redirect(f"/manage_days/?page={page}")
                        return redirect('manage_days')
                    return redirect('calendar_view')
                
                # Validate that dance class fields are provided for new couples
                if not dance_class_stt or not dance_class_lat:
                    messages.warning(request, f'Please provide both Class STT and Class LAT for new couple "{couple_name}"!')
                    if 'manage_days' in referer:
                        if page:
                            return redirect(f"/manage_days/?page={page}")
                        return redirect('manage_days')
                    return redirect('calendar_view')
        
        # Check if couple with this name already exists (for group additions)
        if Couple.objects.filter(name=couple_name, user=request.user).exists():
            messages.warning(request, f'A couple named "{couple_name}" already exists!')
            if redirect_to_manage:
                if page:
                    return redirect(f"/manage_groups/?page={page}")
                return redirect('manage_groups')
            if 'manage_days' in referer:
                if page:
                    return redirect(f"/manage_days/?page={page}")
                return redirect('manage_days')
            return redirect('calendar_view')
        # Check if couple is already in this group (if group_id is provided)
        if group_id:
            group = get_object_or_404(Group, id=group_id, user=request.user)
            if group.couples.filter(name=couple_name, user=request.user).exists():
                messages.warning(request, f'Couple "{couple_name}" is already in group "{group.name}"!')
                if redirect_to_manage:
                    if page:
                        return redirect(f"/manage_groups/?page={page}")
                    return redirect('manage_groups')
                if 'manage_days' in referer:
                    if page:
                        return redirect(f"/manage_days/?page={page}")
                    return redirect('manage_days')
        
        # Create and save the couple
        couple = Couple.objects.create(name=couple_name, min_duration=min_duration, dance_class_stt=dance_class_stt, dance_class_lat=dance_class_lat, user=request.user)

        # Assign to group if provided
        if group_id:
            group = get_object_or_404(Group, id=group_id, user=request.user)
            couple.group = group
            couple.save()
        # Assign to day (ManyToMany) if provided
        if day_id:
            day = get_object_or_404(Day, id=day_id, user=request.user)
            day.couples.add(couple)
        
        messages.success(request, f'Couple "{couple_name}" added successfully!')
        if redirect_to_manage:
            # Preserve paginator page if available
            if page:
                return redirect(f"/manage_groups/?page={page}")
            return redirect('manage_groups')
        # Redirect back to manage_days if that was the referer
        if 'manage_days' in referer:
            if page:
                return redirect(f"/manage_days/?page={page}")
            return redirect('manage_days')
        return redirect('calendar_view')
    # if not POST, just show the page
    return redirect('calendar_view')

@login_required
def delete_couple(request, couple_id):
    """Delete a couple from the database"""
    if request.method == 'POST':
        # Find the couple by ID
        couple = get_object_or_404(Couple, id=couple_id, user=request.user)

        # Delete it
        couple.delete()
        referer = request.META.get('HTTP_REFERER', '')
        redirect_to_manage = 'manage_groups' in referer
        page = request.POST.get('page')
        if redirect_to_manage:
            # Preserve paginator page if available
            if page:
                return redirect(f"/manage_groups/?page={page}")
            return redirect('manage_groups')
    return redirect('calendar_view')

@login_required
def update_couple_name(request, couple_id):
    """Update a couple's name or min_duration or dance class via AJAX (JSON)."""
    if request.method != 'POST':
        return JsonResponse({'error': 'Method not allowed'}, status=405)

    couple = get_object_or_404(Couple, id=couple_id, user=request.user)

    try:
        payload = json.loads(request.body.decode('utf-8'))
    except json.JSONDecodeError:
        return JsonResponse({'error': 'Invalid JSON'}, status=400)

    # Accept either name or min_duration (or both)
    incoming_name = payload.get('name')
    incoming_duration = payload.get('min_duration')
    incoming_dance_class_stt = payload.get('dance_class_stt')
    incoming_dance_class_lat = payload.get('dance_class_lat')
    if incoming_name is None and incoming_duration is None and incoming_dance_class_stt is None and incoming_dance_class_lat is None:
        return JsonResponse({'error': 'No fields to update'}, status=400)

    if incoming_name is not None:
        new_name = str(incoming_name).strip()
        if not new_name:
            return JsonResponse({'error': 'Name cannot be empty'}, status=400)
        if Couple.objects.filter(user=request.user).exclude(id=couple.id).filter(name=new_name).exists():
            return JsonResponse({'error': 'A couple with this name already exists'}, status=409)
        couple.name = new_name

    if incoming_duration is not None:
        try:
            new_duration = int(incoming_duration)
        except (TypeError, ValueError):
            return JsonResponse({'error': 'min_duration must be a number'}, status=400)
        new_duration = int(round(new_duration))
        if new_duration <= 0 or new_duration > 480:
            return JsonResponse({'error': 'min_duration must be between 1 and 480 minutes'}, status=400)
        couple.min_duration = new_duration
    if incoming_dance_class_stt is not None:
        new_dance_class = incoming_dance_class_stt
        if not new_dance_class:
            return JsonResponse({'error': 'Dance Class cannot be empty'}, status=400)
        couple.dance_class_stt = new_dance_class
    if incoming_dance_class_lat is not None:
        new_dance_class = incoming_dance_class_lat
        if not new_dance_class:
            return JsonResponse({'error':'Dance Class cannot be empty'})
        couple.dance_class_lat = incoming_dance_class_lat
    couple.save()

    return JsonResponse({
        'id': couple.id,
        'name': couple.name,
        'min_duration': couple.min_duration,
        'dance_class_stt': couple.dance_class_stt,
        'dance_class_lat': couple.dance_class_lat,
    })
# Trainers

@login_required
def add_trainer(request):
    """Add a new trainer to the database """

    if request.method == 'POST':
        trainer_name = request.POST.get('trainer_name')
        trainer_focus = request.POST.get('trainer_focus')
        if Trainer.objects.filter(name=trainer_name, user=request.user).exists():
            messages.warning(request, f'Trainer "{trainer_name}" already exists')
            return redirect('calendar_view')
        # Create and save the trainer with the default times
        Trainer.objects.create(
            name=trainer_name, 
            start_time=time(8,0), 
            end_time=time(21,0),
            focus=trainer_focus,
            user=request.user,
        )
        return redirect('calendar_view')
    return redirect('calendar_view')

@login_required
def delete_trainer(request, trainer_id):
    """Delete the trainer from the database """
    if request.method == 'POST':
        trainer = get_object_or_404(Trainer, id=trainer_id, user=request.user)

        trainer.delete()

        return redirect('calendar_view')
    return redirect('calendar_view')

@login_required
def update_trainer_name(request, trainer_id):
    """Update a trainer's name"""
    if request.method != "POST":
        return JsonResponse({'error':'Method not allowed'}, status=405)

    trainer = get_object_or_404(Trainer, id=trainer_id, user=request.user)

    try:
        payload = json.loads(request.body.decode('utf-8'))
    except json.JSONDecodeError:
        return JsonResponse({'error':'Invalid JSON'}, status=400)
    
    incoming_name = payload.get('name')
    incoming_focus = payload.get('focus')
    if incoming_name is None and incoming_focus is None:
        return JsonResponse({'error':'No fields to update'}, status=400)
    
    if incoming_name is not None:
        new_name = str(incoming_name).strip()
        if not new_name:
            return JsonResponse({'error':'Name cannot be empty'}, status=400)
        if Trainer.objects.filter(user=request.user).exclude(id=trainer_id).filter(name=new_name).exists():
            return JsonResponse({'error':'A trainer with this name already exists'})
        trainer.name = new_name
    if incoming_focus is not None:
        new_focus = str(incoming_focus).strip()
        if not new_focus:
            return JsonResponse({'error':'Focus cannot be empty'}, status=400)
        trainer.focus = new_focus
    trainer.save()
    return JsonResponse({
        'id':trainer.id,
        'name':trainer.name,
        'focus':trainer.focus,
    })

@login_required
def add_trainer_to_day(request):
    """Adds trainer to the selected day with optional group lesson if times are provided"""
    if request.method == "POST":
        trainer_id = request.POST.get('trainer_id')
        day_id = request.POST.get('day_id')
        start_time = request.POST.get('start_time')
        end_time = request.POST.get('end_time')
        g = request.POST.get('groups')
        if day_id and trainer_id:
            day = get_object_or_404(Day, id=day_id, user=request.user)
            trainer = get_object_or_404(Trainer, id=trainer_id, user=request.user)
            day.trainers.add(trainer)
            day.save()

            # Create/update per-day availability defaulting to the day's bounds
            avail, created = TrainerDayAvailability.objects.update_or_create(
                day=day,
                trainer=trainer,
                defaults={
                    'start_time': day.start_time,
                    'end_time': day.end_time,
                    'user': request.user,
                }
            )
            
            # Only create GroupLesson if both times are provided
            if start_time and end_time:
                try:
                    sh, sm = map(int, start_time.split(":"))
                    eh, em = map(int, end_time.split(":"))
                    start_obj = time(sh, sm)
                    end_obj = time(eh, em)
                except Exception:
                    messages.warning(request, "Invalid time format for the group lesson.")
                    return redirect('calendar_view')

                if start_obj >= end_obj:
                    messages.warning(request, "Start time must be before end time for the group lesson.")
                    return redirect('calendar_view')

                # Check overlap with existing lessons for this trainer on this day
                overlap = False
                for lesson in trainer.group_lesson.filter(day=day):
                    if (start_obj < lesson.time_interval_end) and (end_obj > lesson.time_interval_start):
                        overlap = True
                        break
                try:
                    if ',' in g:
                        aimed_groups = g.split(',')
                    else:
                        aimed_groups = []
                        aimed_groups.append(g)
                    ag = []
                    for aim_group in aimed_groups:
                        ag.append(Group.objects.get(name=aim_group.strip(), user=request.user))
                except Exception as e:
                    print(f'{e}')
                    ag = request.user.owned_groups.all()
                if overlap:
                    messages.warning(request, "This lesson overlaps an existing lesson for this trainer.")
                else:
                    grouplesson = GroupLesson(day=day, time_interval_start=start_obj, time_interval_end=end_obj, user=request.user)
                    grouplesson.save()
                    for x in ag:
                        grouplesson.groups.add(x)
                    trainer.group_lesson.add(grouplesson)
                    trainer.save()
                    messages.success(request, f'Trainer "{trainer.name}" with group lesson added successfully!')     
            if not start_time or not end_time:
                messages.success(request, f'Trainer {trainer} added successfully!')     
            # Determine where to redirect back to
            referer = request.META.get('HTTP_REFERER', '')
            page = request.POST.get('page')

            # Redirect back to manage_days if that was the referer
            if 'manage_days' in referer:
                if page:
                    return redirect(f"/manage_days/?page={page}")
                return redirect('manage_days')
            return redirect('calendar_view')
    # if not POST, just show the page
    return redirect('calendar_view')

@login_required
def update_trainer_time(request, trainer_id):
    """Update a trainer's per-day start/end time via AJAX (JSON).

    Expects JSON with:
      - day_id: int (required)
      - start_time: "HH:MM" (optional)
      - end_time: "HH:MM" (optional)

    Updates TrainerDayAvailability for (day, trainer). Creates one if missing,
    defaulting to the Day's start/end times. Supports partial updates.
    """
    if request.method != 'POST':
        return JsonResponse({'error': 'Method not allowed'}, status=405)

    trainer = get_object_or_404(Trainer, id=trainer_id, user=request.user)
    try:
        payload = json.loads(request.body.decode('utf-8'))
    except json.JSONDecodeError:
        return JsonResponse({'error': 'Invalid JSON'}, status=400)

    day_id = payload.get('day_id')
    if not day_id:
        return JsonResponse({'error': 'day_id is required'}, status=400)
    day = get_object_or_404(Day, id=day_id, user=request.user)

    incoming_start = payload.get('start_time')
    incoming_end = payload.get('end_time')
    if incoming_start is None and incoming_end is None:
        return JsonResponse({'error': 'Provide start_time and/or end_time'}, status=400)

    # Get or create availability defaulting to day's bounds
    availability, created = TrainerDayAvailability.objects.get_or_create(
        day=day, trainer=trainer,
        defaults={'start_time': day.start_time, 'end_time': day.end_time}
    )
    if created or availability.user != request.user:
        availability.user = request.user
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
        return JsonResponse({'error': 'Invalid time format'}, status=400)

    if new_start >= new_end:
        return JsonResponse({'error': 'Start time must be before end time'}, status=400)

    # Optional: enforce within day bounds
    if new_start < day.start_time or new_end > day.end_time:
        return JsonResponse({'error': 'Times must be within day bounds'}, status=400)

    availability.start_time = new_start
    availability.end_time = new_end
    availability.save()

    return JsonResponse({
        'trainer_id': trainer.id,
        'day_id': day.id,
        'start_time': availability.start_time.strftime('%H:%M'),
        'end_time': availability.end_time.strftime('%H:%M'),
    })

# Groups 

@login_required
def manage_groups(request):
    """Display Groups with Paginator"""
    all_groups = request.user.owned_groups.all()

    # Show 2 groups per page
    paginator = Paginator(all_groups, 2)
    page_number = request.GET.get('page', 1)
    page_obj = paginator.get_page(page_number)
    
    # Get error/success messages from query parameters
    error_message = request.GET.get('error', None)
    success_message = request.GET.get('success', None)

    return render(request, 'manage_groups.html', {
        'page_obj':page_obj,
        'groups':page_obj.object_list,
        'error_message': error_message,
        'success_message': success_message,
    })

@login_required
def add_group(request):
    """ Add a new Group to the database """
    if request.method == 'POST':
        group_name = request.POST.get('group_name', '').strip()
        group_index = request.POST.get('group_index', '').strip()
        
        # Check if group already exists (case-insensitive)
        if request.user.owned_groups.filter(name__iexact=group_name).exists():
            messages.warning(request, f'Group "{group_name}" already exists!')
            return redirect('manage_groups')
        
        if not group_name:
            messages.warning(request, 'Group name cannot be empty!')
            return redirect('manage_groups')
        
        # Parse group_index, default to 0 if empty or invalid
        if group_index and group_index.isdigit():
            index_value = int(group_index)
        else:
            index_value = 0
        
        # Create and save the group 
        Group.objects.create(
            name=group_name,
            index=index_value,
            user=request.user,
        )
        
        # Calculate which page the new group is on (2 groups per page)
        total_groups = request.user.owned_groups.count()
        groups_per_page = 2
        last_page = (total_groups + groups_per_page - 1) // groups_per_page
        
        messages.success(request, f'Group "{group_name}" added successfully!')
        return redirect(f'/manage_groups/?page={last_page}')
    return redirect('/manage_groups/')

@login_required
def update_group_name(request, group_id):
    """Update a group's name or index via AJAX (JSON)."""
    if request.method != 'POST':
        return JsonResponse({'error': 'Method not allowed'}, status=405)

    group = get_object_or_404(Group, id=group_id, user=request.user)

    try:
        payload = json.loads(request.body.decode('utf-8'))
    except json.JSONDecodeError:
        return JsonResponse({'error': 'Invalid JSON'}, status=400)

    incoming_name = payload.get('name')
    incoming_index = payload.get('index')
    
    # Update name if provided
    if incoming_name is not None:
        new_name = str(incoming_name).strip()
        if not new_name:
            return JsonResponse({'error': 'Group name cannot be empty'}, status=400)
        # Check if another group already has this name
        if Group.objects.filter(user=request.user).exclude(id=group.id).filter(name__iexact=new_name).exists():
            return JsonResponse({'error': 'A group with this name already exists'}, status=409)
        group.name = new_name
    
    # Update index if provided
    if incoming_index is not None:
        try:
            new_index = int(incoming_index)
            group.index = new_index
        except (ValueError, TypeError):
            return JsonResponse({'error': 'Group index must be a number'}, status=400)
    
    if not incoming_name and not incoming_index:
        return JsonResponse({'error': 'No changes provided'}, status=400)
    
    group.save()

    return JsonResponse({
        'id': group.id,
        'name': group.name,
        'index': group.index,
    })

@login_required
def delete_group(request, group_id):
    """Deletes the Group with its pairs from the database"""
    if request.method == "POST":
        group = get_object_or_404(Group, id=group_id, user=request.user)
        group.delete()
        return redirect('manage_groups')
    return redirect('manage_groups')

@login_required
@require_GET
def manage_groups_fragment(request):
    """Return a fragment HTML for groups on a given page (AJAX)."""
    page_number = request.GET.get('page', 1)
    all_groups = request.user.owned_groups.all()
    paginator = Paginator(all_groups, 2)
    page_obj = paginator.get_page(page_number)
    html = render_to_string('partials/groups_page.html', {
        'page_obj': page_obj,
        'groups': page_obj.object_list,
    }, request=request)
    return JsonResponse({
        'html': html,
        'page': page_obj.number,
        'num_pages': page_obj.paginator.num_pages,
        'has_next': page_obj.has_next(),
        'has_prev': page_obj.has_previous(),
        'next_page': page_obj.next_page_number() if page_obj.has_next() else None,
        'prev_page': page_obj.previous_page_number() if page_obj.has_previous() else None,
    })

@login_required
def move_couple(request):
    """Move a couple to a different goup via AJAX"""
    if request.method != 'POST':
        return JsonResponse({'error': 'Method not allowed'}, status=405)
    
    try:
        payload = json.loads(request.body.decode('utf-8'))
    except json.JSONDecodeError:
        return JsonResponse({'error': 'Invalid JSON'}, status=400)
    
    couple_id = payload.get('couple_id')
    target_group_id = payload.get('target_group_id')

    if not couple_id or not target_group_id:
        return JsonResponse({'error':'Missing couple_id or target_group_id'})
    
    couple = get_object_or_404(Couple, id=couple_id, user=request.user)
    target_group = get_object_or_404(Group, id=target_group_id, user=request.user)

    # Update the couple's group
    couple.group = target_group
    couple.save()

    return JsonResponse({
        'success': True,
        'couple_id': couple.id,
        'couple_name': couple.name,
        'new_group_id': target_group.id,
        'new_group_name': target_group.name,
    })

@login_required
@login_required
def manage_days(request):
    """Display Days"""
    all_days = request.user.day.all()
    groups = request.user.owned_groups.all()
    trainers = request.user.trainer.all()

    # Show 2 days per page
    paginator = Paginator(all_days, 2)
    page_number = request.GET.get('page',1)
    page_obj = paginator.get_page(page_number)

    # Get error/success messages from query parameters 
    error_message = request.GET.get('error', None)
    success_message = request.GET.get('success', None)

    return render(request, 'manage_days.html', {
        'page_obj': page_obj,
        'days': page_obj.object_list,
        'groups': groups,
        'trainers': trainers,
        'error_message': error_message,
        'success_message': success_message,
    })

@login_required
@login_required
def add_day(request):
    """Add a new Day to the database"""
    if request.method == "POST":
        day_name = request.POST.get('day_name', '').strip()
        
        if not day_name:
            return redirect('/manage_days/?error=Day name cannot be empty!')
        
        # Create and save the day
        new_day = Day.objects.create(
            name=day_name,
            user=request.user,
        )

        # Assign all existing couples to this new day so it defaults populated
        for c in Couple.objects.filter(user=request.user):
            new_day.couples.add(c)

        # Caculate which page the new day is on
        total_days = request.user.day.count()
        days_per_page = 2
        last_page = (total_days + days_per_page -1) // days_per_page

        return redirect(f'/manage_days/?page={last_page}&success=Day "{day_name}" added successfully!')
    return redirect('/manage_days/')

@login_required
@login_required
def update_day_name(request, day_id):
    """Update a day's name via AJAX (JSON)"""
    if request.method != 'POST':
        return JsonResponse({'error':'Method not allowed'}, status=405)
    
    day = get_object_or_404(Day, id=day_id, user=request.user)

    try:
        payload = json.loads(request.body.decode('utf-8'))
    except json.JSONDecodeError:
        return JsonResponse({'error':'Invalid JSON'}, status=400)
    
    incoming_name = payload.get('name')

    if incoming_name is None:
        return JsonResponse({'error':'No name provided'}, status=400)
    
    new_name = str(incoming_name).strip()
    if not new_name:
        return JsonResponse({'error':'Day name cannot be empty'}, status=400)
    
    day.name = new_name
    day.save()

    return JsonResponse({
        'id':day.id,
        'name':day.name,
    })

@login_required
@login_required
def delete_day(request, day_id):
    """Delete Day from the database"""
    if request.method == 'POST':
        day = get_object_or_404(Day, id=day_id, user=request.user)
        day.delete()
        return redirect('manage_days')
    return redirect('manage_days')

@login_required
@login_required
def remove_couple_from_day(request, couple_id):
    """Remove a couple's association with a Day (set day to null)."""
    if request.method == 'POST':
        couple = get_object_or_404(Couple, id=couple_id, user=request.user)
        day_id = request.POST.get('day_id')
        if day_id:
            try:
                day = Day.objects.get(id=day_id, user=request.user)
                day.couples.remove(couple)
            except Day.DoesNotExist:
                pass
        
        # Check where the request came from
        referer = request.META.get('HTTP_REFERER', '')
        is_from_manage_days = 'manage_days' in referer
        page = request.POST.get('page')
        
        if is_from_manage_days:
            # Redirect back to manage_days with page if provided
            if page:
                return redirect(f"/manage_days/?page={page}")
            return redirect('manage_days')
        
        # Otherwise redirect to calendar_view
        return redirect('calendar_view')
    return redirect('calendar_view')

@login_required
@login_required
def delete_trainer_from_day(request, trainer_id):
    """Removes trainer from the day"""
    if request.method == 'POST':
        trainer = get_object_or_404(Trainer, id=trainer_id, user=request.user)
        day_id = request.POST.get('day_id')
        if day_id:
            try:
                day = Day.objects.get(id=day_id, user=request.user)
                day.trainers.remove(trainer)
                # Also drop any group lessons for this trainer tied to this day
                lessons = trainer.group_lesson.filter(day=day)
                if lessons.exists():
                    trainer.group_lesson.remove(*lessons)
                    # Delete lessons that are now unused
                    for lesson in lessons:
                        if lesson.trainer.count() == 0:
                            lesson.delete()
                # Remove per-day availability entry
                try:
                    availability = TrainerDayAvailability.objects.get(day=day, trainer=trainer)
                    availability.delete()
                except TrainerDayAvailability.DoesNotExist:
                    pass
            except Day.DoesNotExist:
                pass
        
        referer = request.META.get('HTTP_REFERER', '')
        is_from_manage_days = 'manage_days' in referer
        page = request.POST.get('page')

        if is_from_manage_days:
            if page:
                return redirect(f'/manage_days/?page={page}')
            return redirect('manage_days')
        return redirect('calendar_view')
    return redirect('calendar_view')


@login_required
@login_required
def update_day_time(request, day_id):
    if request.method != 'POST':
        return JsonResponse({'error': 'Method not allowed'}, status=405)
    day = get_object_or_404(Day, id=day_id, user=request.user)
    try:
        payload = json.loads(request.body.decode("utf-8"))
    except:
        return JsonResponse({'error' : 'Invalid JSON'}, status=400)
    
    start = payload.get('start_time')
    end = payload.get('end_time')
    if not start or not end:
        return JsonResponse({'error':'start_time and end_time required'}, status=400)
    try:
        sh, sm = map(int, start.split(":"))
        eh, em = map(int, end.split(":"))
        start_t = time(sh, sm)
        end_t = time(eh, em)
    except Exception:
        return JsonResponse({'error':'Bad time format'}, status=400)
    
    if start_t >= end_t:
        return JsonResponse({'error':'Start must be before end'}, status=400)
    
    # Store old times for comparison
    old_start = day.start_time
    old_end = day.end_time
    
    day.start_time = start_t
    day.end_time = end_t
    day.save(update_fields=['start_time', 'end_time'])
    
    # Update trainer availability intelligently
    # For trainers whose times matched the old day bounds, update to new bounds
    # For trainers with custom times, keep them if within new bounds
    for trainer in day.trainers.all():
        try:
            availability = TrainerDayAvailability.objects.get(day=day, trainer=trainer)
            
            # Check if trainer times were synced with old day times
            trainer_had_default = (availability.start_time == old_start and 
                                   availability.end_time == old_end)
            
            if trainer_had_default:
                # Trainer was using day defaults; update to new day bounds
                availability.start_time = start_t
                availability.end_time = end_t
                availability.save()
            else:
                # Trainer has custom times; keep them if within new bounds
                # If outside, clamp to new bounds
                new_trainer_start = availability.start_time
                new_trainer_end = availability.end_time
                
                if new_trainer_start < start_t:
                    new_trainer_start = start_t
                if new_trainer_end > end_t:
                    new_trainer_end = end_t
                
                # Only update if times changed due to clamping
                if (new_trainer_start != availability.start_time or 
                    new_trainer_end != availability.end_time):
                    availability.start_time = new_trainer_start
                    availability.end_time = new_trainer_end
                    availability.save()
        except TrainerDayAvailability.DoesNotExist:
            pass
    
    return JsonResponse({
        'ok':True,
        'start_time': start,
        'end_time': end
    })

@login_required
@login_required
def delete_group_lesson(request, group_lesson_id):
    """Remove a trainer's lesson association and delete the lesson if unused."""
    if request.method == 'POST':
        lesson = get_object_or_404(GroupLesson, id=group_lesson_id, user=request.user)
        trainer_id = request.POST.get('trainer_id')

        if trainer_id:
            try:
                trainer = Trainer.objects.get(id=trainer_id, user=request.user)
                trainer.group_lesson.remove(lesson)
            except Trainer.DoesNotExist:
                trainer = None

        # If no trainers remain associated, delete the lesson record
        if lesson.trainer.count() == 0:
            lesson.delete()

        referer = request.META.get('HTTP_REFERER', '')
        is_from_manage_days = 'manage_days' in referer
        page = request.POST.get('page')

        if is_from_manage_days:
            if page:
                return redirect(f'/manage_days/?page={page}')
            return redirect('manage_days')
        return redirect('calendar_view')
    return redirect('calendar_view')
            
@login_required
@login_required
@require_GET
def manage_days_fragment(request):
    """Return a fragment HTML for days on a given page (AJAX)"""
    page_number = request.GET.get('page',1)
    all_days = request.user.day.all()
    groups = request.user.owned_groups.all()
    paginator = Paginator(all_days, 2)
    page_obj = paginator.get_page(page_number)
    html = render_to_string('partials/days_groups_page.html', {
        'page_obj': page_obj,
        'days': page_obj.object_list,
        'groups': groups,
    }, request=request)
    return JsonResponse({
        'html': html,
        'page': page_obj.number,
        'num_pages': page_obj.paginator.num_pages,
        'has_next': page_obj.has_next(),
        'has_prev': page_obj.has_previous(),
        'next_page': page_obj.next_page_number() if page_obj.has_next() else None,
        'prev_page': page_obj.previous_page_number() if page_obj.has_previous() else None,
    })

@login_required
@login_required
def move_couple_in_days(request):
    """Move a couple to a different goup via AJAX"""
    if request.method != 'POST':
        return JsonResponse({'error': 'Method not allowed'}, status=405)
    
    try:
        payload = json.loads(request.body.decode('utf-8'))
    except json.JSONDecodeError:
        return JsonResponse({'error': 'Invalid JSON'}, status=400)
    
    couple_id = payload.get('couple_id')
    target_day_id = payload.get('target_day_id')
    source_day_id = payload.get('source_day_id')

    if not couple_id or not target_day_id:
        return JsonResponse({'error':'Missing couple_id or target_day_id'})
    
    couple = get_object_or_404(Couple, id=couple_id, user=request.user)
    target_day = get_object_or_404(Day, id=target_day_id, user=request.user)

    # Add to target day (M2M)
    target_day.couples.add(couple)
    # Remove from source day if provided
    if source_day_id:
        try:
            source_day = Day.objects.get(id=source_day_id, user=request.user)
            source_day.couples.remove(couple)
        except Day.DoesNotExist:
            pass

    return JsonResponse({
        'success': True,
        'couple_id': couple.id,
        'couple_name': couple.name,
        'new_day_id': target_day.id,
        'new_day_name': target_day.name,
    })