
from collections import defaultdict
from datetime import time
import logging
from main.models import Day, TrainerDayAvailability

# Configure logging
logger = logging.getLogger(__name__)

def convert_to_min(time_obj):
    """Converts time(8, 20) to minutes"""
    h = time_obj.hour
    m = time_obj.minute

    minutes = h*60 + m
    return minutes

def min_to_time_str(minutes):
    """Converts minutes to time string HH:MM"""
    h = minutes // 60
    m = minutes % 60
    return f"{h:02d}:{m:02d}"
    
def make_trainers_windows(trainers, day):
    trainers_windows = {}
    for trainer in trainers:
        tda = TrainerDayAvailability.objects.get(trainer=trainer, day=day)
        st = convert_to_min(tda.start_time)
        et = convert_to_min(tda.end_time)
        group_lessons = []
        try:
            for gl in trainer.group_lesson.all():
                x = gl.__str__().split("-")
                stg = convert_to_min(time(int(x[0].split(":")[0]), int(x[0].split(":")[1])))
                etg = convert_to_min(time(int(x[1].split(":")[0]), int(x[1].split(":")[1])))
                group_lessons.append((stg, etg))
        except:
            pass
        
        # Create time windows for this trainer
        time_windows = []
        for i in range(st, et, 30):
            time_str = min_to_time_str(i)
            is_available = True
            
            # Check if this time slot falls within any group lesson
            if group_lessons:
                for gl_start, gl_end in group_lessons:
                    if gl_start <= i < gl_end:
                        is_available = False
                        break
            
            time_windows.append((time_str, is_available))
            
        trainers_windows[trainer] = time_windows
            
    return trainers_windows

def sort_couples_by_class(couples):
    classes = ['A', 'B', 'C', 'D', 'E']
    sorted_couples_lat = defaultdict(list)
    sorted_couples_stt = defaultdict(list)
    for couple in couples:
        name, dance_class_lat, dance_class_stt = couple.name, couple.dance_class_lat, couple.dance_class_stt
        sorted_couples_lat[dance_class_lat].append(couple)
        sorted_couples_stt[dance_class_stt].append(couple)
    
    return sorted_couples_lat, sorted_couples_stt

def sort_couples_by_group(couples, groups):
    """Sort couples by their group's index."""
    sorted_groups = sorted(groups, key=lambda g: g.index)

    # Starts with the non group couples 
    sorted_couples = [c for c in couples if c.group is None]
    for group in sorted_groups:
        group_couples = [c for c in couples if c.group == group]
        sorted_couples.extend(group_couples)
    return sorted_couples

def match_couples_availability(day_dancers_avail, day_times):
    couples_availability = {}

    return couples_availability
def calculate_availability_overlap(couple1_avail, couple2_avail):
    """Calculate percentage of time both couples are available."""
    if not couple1_avail or not couple2_avail:
        return 0.0
    
    total_slots = len(couple1_avail)
    overlap_count = 0

    for i in range(min(len(couple1_avail), len(couple2_avail))):
        if couple1_avail[i][1] and couple2_avail[i][1]:
            overlap_count += 1

    return (overlap_count / total_slots) * 100 if total_slots > 0 else 0.0

def calculate_pairing_score(couple1, couple2, cawt):
    """Score how well two couples can be paired (higher = better)."""
    score = 0

    # 1. Availability overlapt (most important) - 0-100 points
    couple1_avail = cawt.get(couple1.name, [])
    couple2_avail = cawt.get(couple2.name, [])
    overlap = calculate_availability_overlap(couple1_avail, couple2_avail)
    score += overlap

    # 2. Same group bonus - 30 points
    if couple1.group and couple1.group == couple2.group:
        score += 30
    
    # 3. Similar class level bonus - 40 points
    if couple1.dance_class_lat == couple2.dance_class_lat:
        score += 20
    if couple1.dance_class_stt == couple2.dance_class_stt:
        score += 20

    # 4. Limitd availability bonus (prefer pairing constrained couples)
    c1_available_slots = sum(1 for _, avail in couple1_avail if avail)
    c2_available_slots = sum(1 for _, avail in couple2_avail if avail)

    if c1_available_slots < 10:
        score += 15
    
    if c2_available_slots < 10:
        score += 15
    
    return score

def find_best_couple_pairs(couples, cawt, max_pairs=3):
    """FInde the best couples to pair together for group lessons.
    
    Returns list of tuples: [(couple1, couple2, score), ...]
    """
    from itertools import combinations

    pair_scores = []

    # Evaluate all possible pairs
    for couple1, couple2 in combinations(couples, 2):
        score = calculate_pairing_score(couple1, couple2, cawt)

        # Only consider pairs with reasonable overlap (>50 score)
        if score > 50:
            pair_scores.append((couple1, couple2, score))

    # Sort by score (hghest first)
    pair_scores.sort(key=lambda x: x[2], reverse=True)

    return pair_scores[:max_pairs]
def identify_problematic_couples(couples, cawt, available_slots_threshold=8):
    """Identify couples that are hardest to schedule (fewest available slots).
    These should be prioritized for pairing.
    Returns sorted list by constraint level (most constrained first).
    """

    couple_constraints = []
    for couple in couples:
        avail = cawt.get(couple.name, [])
        available_slots = sum(1 for _, is_avail in avail if is_avail)

        couple_constraints.append({
            'couple': couple,
            'available_slots': available_slots,
            'constraint_level': available_slots_threshold - available_slots
        })

    # Sort by constraint level (highest first = most constrained)
    couple_constraints.sort(key=lambda x: x['constraint_level'], reverse=True)

    return couple_constraints

def find_pairs_for_problematic_couples(couples, cawt, max_pairs=5):
    """Find the best pairs specifically for probleatic couples.
    
    Prioritizes pairing difficult-to-schedule couples with compatible partners.
    """
    # Identify problematic couples
    constraints = identify_problematic_couples(couples, cawt)
    problematic_couples = [c['couple'] for c in constraints if c['available_slots'] < 8]

    pairs_scores = []

    # For each problematic couple, find best partner
    for problematic in problematic_couples:
        for partner in couples:
            if partner == problematic:
                continue

            # Check if any already paired
            already_paired = False
            for p in pairs_scores:
                if (problematic == p[0] and partner == p[1]) or \
                    (problematic == p[1] and partner == p[0]):
                    already_paired = True
                    break
            if already_paired:
                continue
            
            score = calculate_pairing_score(problematic, partner, cawt)
            if score > 40:
                pairs_scores.append((problematic, partner, score))
    
    # Sort by score and return
    pairs_scores.sort(key=lambda x: x[2], reverse=True)
    return pairs_scores[:max_pairs]

def create_schedule_with_escalating_pairs(cawt, trainers_windows, couples, day, max_iterations=10000, timeout_seconds=30, max_pair_count=3):
    """Try Scheduling with escalating number of couple pairs.
    Progressively adds pairs until schedule is found
    """

    # Attempt 1: No pairs (original)
    logger.info(f"Attempt 1: Scheduling {len(couples)} couples without pairing...")
    schedule, diagnostics = create_schedule(cawt, trainers_windows, couples, day, max_iterations, timeout_seconds)

    if schedule:
        diagnostics['pairs_used'] = 0
        diagnostics['pairing_strategy'] = 'no_pairs'
        return schedule, diagnostics

    logger.info(f"Failed. Attempting with couple pairs...")

    # Get problematic couples to prioritize
    problematic_pairs = find_pairs_for_problematic_couples(couples, cawt, max_pairs=max_pair_count)

    if not problematic_pairs:
        logger.warning("No viable pairs found for problematic couples.")
        diagnostics['pairs_used'] = 0
        diagnostics['pairing_strategy'] = 'failed_to_find_pairs'
        return None, diagnostics

    # Try with escalating number of pairs
    for num_pairs in range(1, min(max_pair_count+1, len(problematic_pairs)+1)):
        attempt_num = num_pairs + 1
        logger.info(f"\nAttempt {attempt_num}: Trying with {num_pairs} couple pair(s)...")

        # Select top N pairs WITHOUT overlapping couples
        selected_pairs = []
        used_couples = set()
        for c1, c2, score in problematic_pairs:
            if c1 not in used_couples and c2 not in used_couples:
                selected_pairs.append((c1, c2, score))
                used_couples.add(c1)
                used_couples.add(c2)
                if len(selected_pairs) >= num_pairs:
                    break
        
        if len(selected_pairs) < num_pairs:
            logger.debug(f"  ✗ Could only find {len(selected_pairs)} non-overlapping pairs (needed {num_pairs})")
            continue

        # Create modified couples and merged availability
        merged_cawt = dict(cawt)
        modified_couples = list(couples)
        paired_info = []

        # Create PairedCouple class
        class PairedCouple:
            def __init__(self, c1, c2):
                self.name = f"{c1.name} & {c2.name}"
                self.min_duration = max(c1.min_duration, c2.min_duration)
                self.dance_class_lat = c1.dance_class_lat
                self.dance_class_stt = c1.dance_class_stt
                self.is_paired = True
                self.couple1 = c1
                self.couple2 = c2
        
        # Process each pair
        for couple1, couple2, score in selected_pairs:
            logger.debug(f"    Pairing: {couple1.name} + {couple2.name} (score: {score:.1f})")

            # Merge availabilty
            c1_avail = cawt.get(couple1.name, [])
            c2_avail = cawt.get(couple2.name, [])
            merged_avail = []

            for i in range(min(len(c1_avail), len(c2_avail))):
                time_str = c1_avail[i][0]
                both_available = c1_avail[i][1] and c2_avail[i][1]
                merged_avail.append((time_str, both_available))
        
            pair_name = f"{couple1.name} & {couple2.name}"
            merged_cawt[pair_name] = merged_avail

            # Remove individuals, add pair
            modified_couples = [c for c in modified_couples if c != couple1 and c != couple2]
            paired_couple = PairedCouple(couple1, couple2)
            modified_couples.append(paired_couple)
            paired_info.append((couple1.name, couple2.name, score))

        # Try scheduling with this configuration
        schedule, new_diagnostics = create_schedule(merged_cawt, trainers_windows, modified_couples, day, max_iterations, timeout_seconds)
        
        if schedule:
            logger.info(f"  ✓ Success!")
            new_diagnostics['pairs_used'] = num_pairs
            new_diagnostics['pairing_strategy'] = f'{num_pairs}_pairs'
            new_diagnostics['paired_couples'] = paired_info
            return schedule, new_diagnostics
    
    logger.warning("Could not create schedule with any pairing configuration.")
    diagnostics['pairs_used'] = 0
    diagnostics['pairing_strategy'] = 'all_attempts_failed'
    return None, diagnostics
    
def create_schedule(cawt, trainers_windows, couples, day, max_iterations=10000, timeout_seconds=30):
    """Create a schedule for one day with timeout and diagnostics.

    Args:
        cawt: dict mapping couple name -> list of (time_str, is_available) slots (typically coarse, e.g., 30-min)
        trainers_windows: dict mapping Trainer -> list of 5-min (time_str, is_available)
        couples: ordered list of Couple objects to schedule
        max_iterations: maximum backtracking iterations before giving up
        timeout_seconds: maximum time in seconds before giving up
    
    Returns:
        tuple: (schedule_dict, diagnostics_dict)
    """
    import time
    
    start_time = time.time()
    iterations = [0]  # Use list to allow modification in nested function
    progress_tracker = {'highest_idx': -1, 'stall_count':0, 'last_progress_time': start_time}

    # Adaptive timeout based on couples count
    if timeout_seconds == 30:
        adaptive_timeout = max(10, 5 + len(couples) * 2.5)
        timeout_seconds = min(adaptive_timeout, 60)
    # Precompute availability intervals per couple so we can block any overlap, not just matching exact timestamps.
    couple_intervals = {}
    for name, slots in cawt.items():
        if not slots:
            continue
        # Infer slot length from consecutive entries (fallback to 30 minutes).
        slot_lengths = []
        for i in range(len(slots) - 1):
            h1, m1 = map(int, slots[i][0].split(':'))
            h2, m2 = map(int, slots[i + 1][0].split(':'))
            diff = (h2 * 60 + m2) - (h1 * 60 + m1)
            if diff > 0:
                slot_lengths.append(diff)
        default_slot = min(slot_lengths) if slot_lengths else 30

        intervals = []
        for i, (time_str, avail) in enumerate(slots):
            h, m = map(int, time_str.split(':'))
            start = h * 60 + m
            if i + 1 < len(slots):
                h2, m2 = map(int, slots[i + 1][0].split(':'))
                end = h2 * 60 + m2
            else:
                end = start + default_slot
            intervals.append((start, end, avail))
        couple_intervals[name] = intervals
    
    solution = {}
    failed_couples = []  # Track couples that couldn't be scheduled

    def backtrack(idx = 0):
        iterations[0] += 1
        current_time = time.time()
        
        # Check timeout and iteration limit
        if iterations[0] > max_iterations or current_time - start_time > timeout_seconds:
            return False
            
        if idx == len(couples):
            return True

        if idx > progress_tracker['highest_idx']:
            progress_tracker['highest_idx'] = idx
            progress_tracker['stall_count'] = 0
            progress_tracker['last_progress_time'] = current_time
        else:
            progress_tracker['stall_count'] += 1
        
        # Early exit if stuck (no progress for too long)
        if progress_tracker['stall_count'] > 5000: #Too many attempts at same level
            logger.debug(f"    Stuck at couple {idx+1}, moving on...")
            return False
        
        if current_time - progress_tracker['last_progress_time'] > 5:
            logger.debug(f"    No progress for 5s at couple {idx+1}, moving on...")
            return False
        p = couples[idx]
        name = p.name
        lesson_time = [p.min_duration]
        
        couple_tried = False
        for trainer in trainers_windows:
            # time slots
            ts = trainers_windows[trainer]

            for i, (time_str, is_available) in enumerate(ts):
                if not is_available:
                    continue
                
                # convert time_tr to minutes
                h, m = map(int, time_str.split(':'))
                start_min = h * 60 + m
                for duration in lesson_time:
                    p.min_duration = duration
                    end_min = start_min + duration

                    # Check whether couple is available for the entire lesson interval.
                    couple_available = True
                    intervals = couple_intervals.get(name, [])
                    for slot_start, slot_end, avail in intervals:
                        overlap = not (slot_end <= start_min or slot_start >= end_min)
                        # Couple must be available for ALL overlapping slots
                        if overlap and not avail:
                            couple_available = False
                            break
                        # Also ensure we have a record for this couple
                        if overlap and len(intervals) == 0:
                            couple_available = False
                            break
                    if not couple_available:
                        continue

                    # Check if all trainer slots in this time range are available
                    can_schedule = True
                    slots_to_mark = []

                    # Calculate how many 5-minutes are needed
                    num_slots = (duration + 4) // 5 # Round up

                    for j in range(i, min(i + num_slots, len(ts))):
                        t_str, t_avail = ts[j]
                        if not t_avail:
                            can_schedule = False
                            break
                        slots_to_mark.append(j)
                    tda = TrainerDayAvailability.objects.get(trainer=trainer, day=day)
                    if end_min > convert_to_min(tda.end_time):
                        can_schedule = False
                    if not can_schedule:
                        continue

                    # Mark slots as unavailable
                    for j in slots_to_mark:
                        ts[j] = (ts[j][0], False)
                        
                    solution[p] = (trainer, time_str)
                    couple_tried = True

                    # Recurse to next couple
                    if backtrack(idx + 1):
                        return True

                    # Backtrack: undo changes
                    del solution[p]
                    for j in slots_to_mark:
                        ts[j] = (ts[j][0], True)
        
        # If we couldn't schedule this couple at all
        if not couple_tried and name not in [c['couple'] for c in failed_couples]:
            failed_couples.append({
                'couple': name,
                'reason': 'No available slots match couple availability'
            })
        
        return False

    # Start the backtrack 
    success = backtrack(0)
    
    # Prepare diagnostics
    diagnostics = {
        'iterations': iterations[0],
        'time_taken': round(time.time() - start_time, 2),
        'failed_couples': failed_couples,
        'scheduled_count': len(solution),
        'total_couples': len(couples),
        'timeout': iterations[0] > max_iterations or (time.time() - start_time > timeout_seconds)
    }
    
    return (solution, diagnostics) if success else (None, diagnostics)

def create_schedule_with_pairing(cawt, trainers_windows, couples, day, max_iterations=10000, timeout_seconds = 30):
    """Try scheduling with automatic couple pairing if needed."""

    # First attemp: normal scheduling
    schedule, diagnostics = create_schedule(cawt, trainers_windows, couples, day, max_iterations, timeout_seconds)

    if schedule:
        return schedule, diagnostics
    
    # If failed, try with pairing
    print(f"Initial scheduling failed for {day.name}. Analyzing couple pairings...")

    # Find best pairs
    best_pairs = find_best_couple_pairs(couples, cawt, max_pairs=5)

    if not best_pairs:
        print("No viable couple pairs found.")
        diagnostics['pairing_attempted'] = True
        diagnostics['paired_couples'] = []
        return None, diagnostics

    print(f"Found {len(best_pairs)} potential pairings to try...")

    # Try scheduling with each pairing option
    for couple1, couple2, score in best_pairs:
        print(f"    Trying pair: {couple1.name} + {couple2.name} (score: {score:.1f})")

        # Create mergedd availability for the pair
        merged_cawt = dict(cawt)
        pair_name = f"{couple1.name} & {couple2.name}"

        # Merge Availability (both must be available)
        c1_avail = cawt.get(couple1.name, [])
        c2_avail = cawt.get(couple2.name, [])
        merged_avail = []

        for i in range(min(len(c1_avail), len(c2_avail))):
            time_str = c1_avail[i][0]
            both_available = c1_avail[i][1] and c2_avail[i][1]
            merged_avail.append((time_str, both_available))

        merged_cawt[pair_name] = merged_avail

        # Remove individual couples and add merged pair
        modified_couples = [c for c in couples if c != couple1 and c != couple2]

        class PairedCouple:
            def __init__(self, c1, c2):
                self.name = f"{c1.name} & {c2.name}"
                self.min_duration = max(c1.min_duration, c2.min_duration)
                self.dance_class_lat = c1.dance_class_lat
                self.dance_class_stt = c1.dance_class_stt
                self.is_paired = True
                self.couple1 = c1
                self.couple2 = c2

        paired_couple = PairedCouple(couple1, couple2)
        modified_couples.append(paired_couple)

        # Try scheduling with this configuration
        schedule, new_diagnostics = create_schedule(merged_cawt, trainers_windows, modified_couples, day, max_iterations, timeout_seconds)

        if schedule:
            print(f"  ✓ Schedule created with pairing!")
            new_diagnostics['pairing_attempted'] = True
            new_diagnostics['paired_couples'] = [(couple1.name, couple2.name, score)]
            return schedule, new_diagnostics
    
    print("Could not create schedule even with pairing.")
    diagnostics['pairing_attempted'] = True
    diagnostics['paired_couples'] = []
    return None, diagnostics
