from collections import defaultdict
from datetime import time
import logging
from main.models import Day, TrainerDayAvailability

logger = logging.getLogger(__name__)

def convert_to_min(time_obj):
    h = time_obj.hour
    m = time_obj.minute
    return h*60 + m

def min_to_time_str(minutes):
    h = minutes // 60
    m = minutes % 60
    return f"{h:02d}:{m:02d}"

def time_str_to_min(time_str):
    h, m = map(int, time_str.split(':'))
    return h * 60 + m

def compute_couple_options(couple, cawt, trainers_windows, day):
    """Spočíta, koľko reálnych možností má pár (tréner, čas).
    
    NOTE: Trainer windows use 5-minute slots, but couple availability uses 30-minute slots.
    We need to convert couple slots to time ranges to check for overlap.
    """
    name = couple.name
    couple_slots = cawt.get(name, [])
    if not couple_slots:
        return 0

    # Infer slot length from couple availability (typically 30 minutes)
    slot_length = 30  # Default to 30-minute slots
    if len(couple_slots) > 1:
        h1, m1 = map(int, couple_slots[0][0].split(':'))
        h2, m2 = map(int, couple_slots[1][0].split(':'))
        diff = (h2 * 60 + m2) - (h1 * 60 + m1)
        if diff > 0:
            slot_length = diff

    # Convert couple availability to time intervals
    intervals = []
    current_start = None
    last_min = None
    for time_str, is_avail in couple_slots:
        t_min = time_str_to_min(time_str)
        if is_avail:
            if current_start is None:
                current_start = t_min
            last_min = t_min
        else:
            if current_start is not None:
                intervals.append((current_start, last_min + slot_length))
                current_start = None
    if current_start is not None:
        intervals.append((current_start, last_min + slot_length))

    total_options = 0
    for trainer, windows in trainers_windows.items():
        # Get trainer's working hours
        tda = TrainerDayAvailability.objects.get(trainer=trainer, day=day)
        trainer_start = convert_to_min(tda.start_time)
        trainer_end = convert_to_min(tda.end_time)

        for start, end in intervals:
            # Intersection with trainer's day
            s = max(start, trainer_start)
            e = min(end, trainer_end)
            if e - s >= couple.min_duration:
                # Count possible starts: trainer windows are 5-minute slots
                possible_starts = max(1, (e - s - couple.min_duration) // 5 + 1)
                total_options += possible_starts
    return total_options

def order_couples_by_difficulty(couples, cawt, trainers_windows, day):
    couples_with_score = []
    for c in couples:
        options = compute_couple_options(c, cawt, trainers_windows, day)
        couples_with_score.append((c, options))
    
    # Najprv páry s najmenej možnosťami
    couples_with_score.sort(key=lambda x: x[1])
    ordered = [c for c, _ in couples_with_score]
    return ordered

def backtracking_schedule(cawt, trainers_windows, couples, day, hard_timeout=30, max_iterations=100000):
    """Backtracking schedule algorithm.
    
    Trainer windows use 5-minute slots, but couple availability uses 30-minute slots.
    We convert couple slots to intervals and check for overlap properly.
    """
    import time
    start_time = time.time()
    iterations = [0]
    solution = {}
    
    # Copy trainer slots for modification
    trainer_slots = {
        t: list(windows) for t, windows in trainers_windows.items()
    }

    # Map couple names to objects
    name_to_couple = {c.name: c for c in couples}

    # Precompute couple availability as intervals
    couple_intervals = {}
    for name, slots in cawt.items():
        if not slots:
            continue
        # Infer slot length from consecutive entries
        slot_length = 30  # Default
        if len(slots) > 1:
            h1, m1 = map(int, slots[0][0].split(':'))
            h2, m2 = map(int, slots[1][0].split(':'))
            diff = (h2 * 60 + m2) - (h1 * 60 + m1)
            if diff > 0:
                slot_length = diff
        
        # Convert to intervals
        intervals = []
        for i, (time_str, avail) in enumerate(slots):
            h, m = map(int, time_str.split(':'))
            start = h * 60 + m
            end = start + slot_length
            intervals.append((start, end, avail))
        couple_intervals[name] = intervals

    def can_place(couple, trainer, start_idx):
        """Check if we can place a couple starting at this trainer slot index."""
        windows = trainer_slots[trainer]
        duration = couple.min_duration
        
        # Need to cover 'duration' minutes with 5-minute slots
        needed_slots = (duration + 4) // 5  # Round up

        if start_idx + needed_slots > len(windows):
            return False, []

        # Get couple's availability intervals
        couple_avail_intervals = couple_intervals.get(couple.name, [])
        if not couple_avail_intervals:
            return False, []

        # Calculate the lesson time range
        start_time_str, _ = windows[start_idx]
        start_min = time_str_to_min(start_time_str)
        end_min = start_min + duration

        # Check couple availability: must be available for entire duration
        couple_available = True
        for interval_start, interval_end, avail in couple_avail_intervals:
            # Check if lesson overlaps with this interval
            overlap = interval_start < end_min and interval_end > start_min
            if overlap and not avail:
                couple_available = False
                break
        
        if not couple_available:
            return False, []

        # Verify we have couple availability covering the entire lesson
        overlapping_ends = [interval_end for interval_start, interval_end, avail in couple_avail_intervals
                           if interval_start < end_min and interval_end > start_min]
        if not overlapping_ends or max(overlapping_ends) < end_min:
            couple_available = False
            return False, []

        # Check trainer availability for all needed slots
        slots_to_use = []
        for j in range(start_idx, start_idx + needed_slots):
            if j >= len(windows):
                return False, []
            _, trainer_free = windows[j]
            if not trainer_free:
                return False, []
            slots_to_use.append(j)

        return True, slots_to_use

    def backtrack(idx):
        iterations[0] += 1
        if iterations[0] > max_iterations or time.time() - start_time > hard_timeout:
            return False
        if idx == len(couples):
            return True

        couple = couples[idx]

        # Heuristic: sort trainers by free slots (most free first)
        trainers_ordered = sorted(
            trainer_slots.keys(),
            key=lambda t: sum(1 for _, free in trainer_slots[t] if free),
            reverse=True
        )

        for trainer in trainers_ordered:
            windows = trainer_slots[trainer]
            for i, (time_str, is_free) in enumerate(windows):
                if not is_free:
                    continue

                can_sched, slots_to_use = can_place(couple, trainer, i)
                if not can_sched:
                    continue

                # Mark slots as occupied
                for j in slots_to_use:
                    t_str, _ = windows[j]
                    windows[j] = (t_str, False)

                solution[couple] = (trainer, windows[slots_to_use[0]][0])

                if backtrack(idx + 1):
                    return True

                # Backtrack: undo changes
                del solution[couple]
                for j in slots_to_use:
                    t_str, _ = windows[j]
                    windows[j] = (t_str, True)

        return False

    success = backtrack(0)
    diagnostics = {
        'iterations': iterations[0],
        'time_taken': round(time.time() - start_time, 2),
        'success': success,
        'scheduled_count': len(solution),
        'total_couples': len(couples),
        'used_backtracking': True
    }
    return solution if success else None, diagnostics

def greedy_schedule(cawt, trainers_windows, couples, day):
    """
    Greedy fallback algorithm that always returns the best possible partial schedule.
    Schedules as many couples as possible.
    
    Trainer windows use 5-minute slots, but couple availability uses 30-minute slots.
    """

    # Copy trainer slots for modification
    trainer_slots = {t: list(windows) for t, windows in trainers_windows.items()}

    solution = {}
    unscheduled = []

    # Sort couples by available slots (most constrained first)
    def count_available(couple):
        return sum(1 for _, a in cawt.get(couple.name, []) if a)

    couples_sorted = sorted(couples, key=count_available)

    # Precompute couple availability as intervals
    couple_intervals = {}
    for name, slots in cawt.items():
        if not slots:
            continue
        # Infer slot length
        slot_length = 30  # Default
        if len(slots) > 1:
            h1, m1 = map(int, slots[0][0].split(':'))
            h2, m2 = map(int, slots[1][0].split(':'))
            diff = (h2 * 60 + m2) - (h1 * 60 + m1)
            if diff > 0:
                slot_length = diff
        
        # Convert to intervals
        intervals = []
        for i, (time_str, avail) in enumerate(slots):
            h, m = map(int, time_str.split(':'))
            start = h * 60 + m
            end = start + slot_length
            intervals.append((start, end, avail))
        couple_intervals[name] = intervals

    for couple in couples_sorted:
        placed = False
        duration = couple.min_duration
        needed_slots = (duration + 4) // 5  # 5-minute slots needed

        couple_avail_intervals = couple_intervals.get(couple.name, [])
        if not couple_avail_intervals:
            unscheduled.append(couple)
            continue

        # Try all trainers
        for trainer, windows in trainer_slots.items():

            # Try all possible starts (leaving room for needed slots)
            for i in range(len(windows) - needed_slots + 1):

                # Check trainer availability for all needed slots
                trainer_ok = all(windows[j][1] for j in range(i, i + needed_slots))
                if not trainer_ok:
                    continue

                # Calculate lesson time range
                start_time_str = windows[i][0]
                start_min = time_str_to_min(start_time_str)
                end_min = start_min + duration

                # Check couple availability: must be available for entire duration
                couple_available = True
                for interval_start, interval_end, avail in couple_avail_intervals:
                    # Check if lesson overlaps with this interval
                    overlap = interval_start < end_min and interval_end > start_min
                    if overlap and not avail:
                        couple_available = False
                        break
                
                if not couple_available:
                    continue

                # Verify we have couple availability covering entire lesson
                overlapping_ends = [interval_end for interval_start, interval_end, avail in couple_avail_intervals
                                   if interval_start < end_min and interval_end > start_min]
                if not overlapping_ends or max(overlapping_ends) < end_min:
                    continue

                # Schedule the couple
                for j in range(i, i + needed_slots):
                    t_str, _ = windows[j]
                    windows[j] = (t_str, False)

                solution[couple] = (trainer, windows[i][0])
                placed = True
                break

            if placed:
                break

        if not placed:
            unscheduled.append(couple)

    diagnostics = {
        "strategy": "greedy_partial",
        "scheduled_count": len(solution),
        "unscheduled_count": len(unscheduled),
        "unscheduled": [c.name for c in unscheduled],
        "total_couples": len(couples),
        "used_backtracking": False
    }

    return solution, diagnostics

def build_schedule(cawt, trainers_windows, couples, day, hard_timeout=30):
    """Nový scheduling engine:
    1) zoradí páry podľa náročnosti
    2) skúsi inteligentný backtracking
    3) ak zlyhá, použije greedy fallback
    """

    # 1. Zoradenie párov
    ordered_couples = order_couples_by_difficulty(couples, cawt, trainers_windows, day)

    # 2. Skús backtracking
    schedule, diag_bt = backtracking_schedule(
        cawt=cawt,
        trainers_windows=trainers_windows,
        couples=ordered_couples,
        day=day,
        hard_timeout=hard_timeout
    )

    if schedule:
        diag_bt['strategy'] = 'backtracking'
        return schedule, diag_bt

    logger.warning(f"Backtracking pre {day.name} zlyhal, prechádzam na greedy fallback...")
    print(f'cawt:{cawt}, trainers_windows:{trainers_windows}, couples:{ordered_couples}, day:{day}')
    # 3. Greedy fallback
    schedule_g, diag_g = greedy_schedule(
        cawt=cawt,
        trainers_windows=trainers_windows,
        couples=ordered_couples,
        day=day
    )

    diag_g['strategy'] = 'greedy_fallback'
    # Edted 11.5
    # return schedule_g if schedule_g else None, diag_g
    return schedule_g, diag_g
