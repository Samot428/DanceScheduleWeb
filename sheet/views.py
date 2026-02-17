from django.shortcuts import render, get_object_or_404, redirect
from django.http import JsonResponse
from .models import SheetCell
from TrainerClubs.models import Club
from main.models import Day, Group
from datetime import date, timedelta, datetime
from django.contrib.auth.decorators import login_required
import json
import copy
NUM_COLS = 26

@login_required
def club_redirect(request, club_id):
    club = get_object_or_404(Club, id=club_id)
    if request.user.userprofile.user_type == 'trainer':
        return redirect(f"/club/{club.id}/")
    return redirect(f"/dancer/club/{club.id}/")

@login_required
def dashboard_redirect(request):
    if request.user.userprofile.user_type == 'trainer':
        return redirect("/trainer/trainer_dashboard/")
    return redirect("/dancer/dancers_dashboard/")

def col_name(index):
    name = ""
    while index >= 0:
        name = chr(index % 26 + 65) + name
        index = index // 26 - 1
    return name

def day_and_time_slots(days, interval_minutes=30):
    """Returns time slots for each day in given interval"""
    slots = []
    dslots = []
    slots.append("")
    dslots.append("")
    for day in days:
        start_dt = datetime.combine(date.today(), day.start_time)
        end_dt = datetime.combine(date.today(), day.end_time)
        while start_dt <= end_dt:
            if day.name not in dslots:
                dslots.append(day.name)
            else:
                dslots.append("")
            slots.append(start_dt.strftime("%H:%M"))
            start_dt += timedelta(minutes=interval_minutes)
        dslots.append("")
        slots.append("")  # separator between days
    return slots, dslots

@login_required 
def sheet_view(request, club_id):
    club = get_object_or_404(Club, id=club_id)
    groups = Group.objects.filter(club=club).all()
    days = Day.objects.filter(club=club).all()

    tslots, dslots = day_and_time_slots(days=days)
    NUM_ROWS = len(tslots)
    height_per_row = 0
    sheets = {}
    for group in groups:
        cells = SheetCell.objects.filter(club=club, group=group)

        rows = {}
        for cell in cells:
            rows.setdefault(cell.row, {})[cell.col] = {
                "value": cell.value,
                "color": cell.color
            }

        # Vytvor rowData pre túto group
        row_data = []
        for i in range(NUM_ROWS):
            row = {
                "row_id": i,
                "day": dslots[i],
                "time": tslots[i]
            }

            for c in range(NUM_COLS):
                col = col_name(c)
                row[col] = rows.get(i, {}).get(col, {}).get("value", "")
                row[col + "_color"] = rows.get(i, {}).get(col, {}).get("color", "")

            row_data.append(row)
        height_per_row = len(row_data) * 31
        sheets[group.name] = copy.deepcopy(row_data)

    return render(request, "sheet.html", {
        "sheets_json": json.dumps(sheets),
        "groups_json": json.dumps([g.name for g in groups]),
        "groups": [g.name for g in groups], 
        "club": club,
        "height_per_row": height_per_row,
        "user_type": request.user.userprofile.user_type,
    })

def get_sheet_data(request, club_id, group_name):
    """Returns all cells for a specific sheet/group as JSON"""
    try:
        group = Group.objects.get(name=group_name, club_id=club_id)
    except Group.DoesNotExist:
        return JsonResponse({"error": "Group not found"}, status=404)
    
    cells = SheetCell.objects.filter(club_id=club_id, group=group)
    
    # Build row data structure
    row_data = {}
    for cell in cells:
        row_id = cell.row
        col = cell.col
        
        if row_id not in row_data:
            row_data[row_id] = {"row_id": row_id}
        
        row_data[row_id][col] = cell.value
        row_data[row_id][col + "_color"] = cell.color
    
    # Convert to list sorted by row_id
    result = sorted(row_data.values(), key=lambda x: x["row_id"])
    
    return JsonResponse(result, safe=False)
