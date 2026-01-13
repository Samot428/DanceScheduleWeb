from django.shortcuts import render, get_object_or_404, redirect
from .models import SheetCell
from TrainerClubs.models import Club
from main.models import Day
from datetime import date, timedelta, datetime
import json
NUM_COLS = 26

def club_redirect(request, club_id):
    club = get_object_or_404(Club, id=club_id)
    if request.user.userprofile.user_type == 'trainer':
        return redirect(f"/club/{club.id}/")
    return redirect(f"/dancer/club/{club.id}/")

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
    
def sheet_view(request, club_id):
    club = get_object_or_404(Club, id=club_id)
    days = Day.objects.filter(club=club).all()
    cells = SheetCell.objects.filter(club=club)

    tslots, dslots = day_and_time_slots(days=days)
    NUM_ROWS = len(tslots)
    rows = {}
    for cell in cells:
        rows.setdefault(cell.row, {})[cell.col] = {
            "value": cell.value,
            "color": cell.color
        }

    row_data = []
    for i in range(NUM_ROWS):
        row = {"row_id": i, "day":dslots[i], "time":tslots[i]}

        for c in range(NUM_COLS):
            col = col_name(c)
            row[col] = rows.get(i, {}).get(col, {}).get("value", "")
            row[col + "_color"] = rows.get(i, {}).get(col, {}).get("color", "")

        row_data.append(row)
    return render(request, "sheet.html", {
        "row_data_json": json.dumps(row_data),
        "club": club,
        "user_type": request.user.userprofile.user_type,
        "height_per_row": len(row_data) * 31
    })