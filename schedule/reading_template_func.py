from collections import defaultdict
from datetime import datetime, date, timedelta, time

from sheet.models import SheetCell
from main.models import Group, Club, Day


NUM_COLS = 26


def col_name(index):
    """Convert 0 → A, 1 → B, ..., 25 → Z"""
    name = ""
    while index >= 0:
        name = chr(index % 26 + 65) + name
        index = index // 26 - 1
    return name


def day_and_time_slots(days, interval_minutes=30):
    """
    Same logic as sheet_view – must stay identical!
    """
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
        slots.append("")

    return slots, dslots


def is_shade_of_white(color):
    """Check if a color is white/light (unavailable)"""
    if not color:
        return True

    color = color.replace("#", "")

    if len(color) >= 6:
        hex_color = color[-6:]
    else:
        return True

    try:
        r = int(hex_color[0:2], 16)
        g = int(hex_color[2:4], 16)
        b = int(hex_color[4:6], 16)
    except Exception:
        return True

    return r > 200 and g > 200 and b > 200


def read_dancers_availability_from_template(club_id, group_name):
    """
    Reads dancer availability from your AG Grid template.

    Returns:
        day_times: dict { day_name: [time objects] }
        day_dancers_avail:
            dict {
                day_name: {
                    dancer_name: [True/False per time slot]
                }
            }
    """

    try:
        club = Club.objects.get(id=club_id)
        group = Group.objects.get(name=group_name, club=club)
    except (Club.DoesNotExist, Group.DoesNotExist):
        return {}, {}

    # --- 1️⃣ Rebuild full grid structure (same as sheet_view) ---

    days = Day.objects.filter(club=club).order_by("id")
    tslots, dslots = day_and_time_slots(days)
    NUM_ROWS = len(tslots)

    # Build empty grid
    grid = []
    for i in range(NUM_ROWS):
        row = {
            "row_id": i,
            "day": dslots[i],
            "time": tslots[i],
        }

        # Prepare dancer columns
        for c in range(NUM_COLS):
            col = col_name(c)
            row[col] = ""
            row[col + "_color"] = ""

        grid.append(row)

    # --- 2️⃣ Overlay saved SheetCell data ---

    cells = SheetCell.objects.filter(club=club, group=group)

    for cell in cells:
        row_idx = cell.row
        col = cell.col

        if 0 <= row_idx < NUM_ROWS:
            grid[row_idx][col] = cell.value
            grid[row_idx][col + "_color"] = cell.color

    # --- 3️⃣ Extract dancer names from header row (row 0) ---

    header_row = grid[0]

    dancer_columns = []
    dancer_names = []

    for c in range(NUM_COLS):
        col = col_name(c)
        name = header_row.get(col)

        if name:
            dancer_columns.append(col)
            dancer_names.append(name)

    # --- 4️⃣ Parse availability ---

    day_times = defaultdict(list)
    day_dancers_avail = defaultdict(lambda: defaultdict(list))

    current_day = None

    for row in grid[1:]:  # skip header row

        if row["day"]:
            current_day = row["day"]

        if not current_day:
            continue

        time_str = row["time"]
        if not time_str:
            continue

        try:
            h, m = time_str.split(":")
            t = time(int(h), int(m))
        except Exception:
            continue

        day_times[current_day].append(t)

        for col, dancer in zip(dancer_columns, dancer_names):
            color = row.get(col + "_color", "")
            available = not is_shade_of_white(color)
            day_dancers_avail[current_day][dancer].append(available)

    return dict(day_times), {
        day: dict(dancers)
        for day, dancers in day_dancers_avail.items()
    }
