from django.shortcuts import render, get_object_or_404
from .models import SheetCell
from TrainerClubs.models import Club

NUM_ROWS = 100
NUM_COLS = 26

def col_name(index):
    name = ""
    while index >= 0:
        name = chr(index % 26 + 65) + name
        index = index // 26 - 1
    return name

def sheet_view(request, club_id):
    club = get_object_or_404(Club, id=club_id)
    cells = SheetCell.objects.filter(club=club)

    rows = {}
    for cell in cells:
        rows.setdefault(cell.row, {})[cell.col] = {
            "value": cell.value,
            "color": cell.color
        }

    row_data = []
    for i in range(NUM_ROWS):
        row = {"row_id": i}

        for c in range(NUM_COLS):
            col = col_name(c)
            row[col] = rows.get(i, {}).get(col, {}).get("value", "")
            row[col + "_color"] = rows.get(i, {}).get(col, {}).get("color", "")

        row_data.append(row)

    return render(request, "sheet.html", {
        "row_data": row_data,
        "club": club,
    })


