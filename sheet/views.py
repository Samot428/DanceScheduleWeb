from django.shortcuts import render
from .models import SheetCell

NUM_ROWS = 20

def sheet_view(request):
    cells = SheetCell.objects.all()

    rows = {}
    for cell in cells:
        rows.setdefault(cell.row, {})[cell.col] = {
            "value": cell.value,
            "color": cell.color
        }

    row_data = []
    for i in range(NUM_ROWS):
        row_data.append({
            "row_id": i,
            "a": rows.get(i, {}).get("a", {}).get("value", ""),
            "a_color": rows.get(i, {}).get("a", {}).get("color", ""),
            "b": rows.get(i, {}).get("b", {}).get("value", ""),
            "b_color": rows.get(i, {}).get("b", {}).get("color", ""),
        })


    return render(request, "sheet.html", {
        "row_data": row_data,
    })

