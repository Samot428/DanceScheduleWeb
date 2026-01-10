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
    """Spočíta, koľko reálnych možností má pár (tréner, čas)."""
    name = couple.name
    couple_slots = cawt.get(name, [])
    if not couple_slots:
        return 0

    # Predpočítaj dostupnosť páru ako intervaly
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
                intervals.append((current_start, last_min + 5))
                current_start = None
    if current_start is not None:
        intervals.append((current_start, last_min + 5))

    total_options = 0
    for trainer, windows in trainers_windows.items():
        # zober trénerovu dostupnosť ako intervaly
        tda = TrainerDayAvailability.objects.get(trainer=trainer, day=day)
        trainer_start = convert_to_min(tda.start_time)
        trainer_end = convert_to_min(tda.end_time)

        for start, end in intervals:
            # prienik s trénerovým dňom
            s = max(start, trainer_start)
            e = min(end, trainer_end)
            if e - s >= couple.min_duration:
                # počet možných začiatkov v tomto intervale
                total_options += max(1, (e - s - couple.min_duration) // 5 + 1)
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
    import time
    start_time = time.time()
    iterations = [0]
    solution = {}
    
    # Pre lepšiu efektivitu si spravíme kópiu slotov trénerov
    trainer_slots = {
        t: list(windows) for t, windows in trainers_windows.items()
    }

    # Pre pohodlnosť: map name -> couple
    name_to_couple = {c.name: c for c in couples}

    def can_place(couple, trainer, start_idx):
        """Skontroluje, či môžeme pár umiestniť na trénera od indexu start_idx."""
        windows = trainer_slots[trainer]
        duration = couple.min_duration
        needed_slots = (duration + 4) // 5

        if start_idx + needed_slots > len(windows):
            return False, []

        # čas páru
        couple_avail = cawt.get(couple.name, [])
        if not couple_avail:
            return False, []

        # nájdi index v couple_avail podľa time_str
        slots_to_use = []
        for j in range(start_idx, start_idx + needed_slots):
            time_str, trainer_free = windows[j]
            if not trainer_free:
                return False, []
            
            # nájdeme stav páru v tomto čase
            matched = False
            for t_str, is_avail in couple_avail:
                if t_str == time_str:
                    if not is_avail:
                        return False, []
                    matched = True
                    break
            if not matched:
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

        # Heuristika: trénerov zoradíme podľa počtu voľných slotov (najviac voľný prvý)
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

                # označ slots ako obsadené
                for j in slots_to_use:
                    t_str, _ = windows[j]
                    windows[j] = (t_str, False)

                solution[couple] = (trainer, windows[slots_to_use[0]][0])

                if backtrack(idx + 1):
                    return True

                # undo
                for j in slots_to_use:
                    t_str, _ = windows[j]
                    windows[j] = (t_str, True)
                del solution[couple]

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
    Greedy fallback, ktorý vždy vráti najlepší možný čiastočný rozvrh.
    Naplánuje maximum párov, ktoré sa dajú umiestniť.
    """

    # Kópia trénerových slotov, aby sme ich mohli označovať ako obsadené
    trainer_slots = {t: list(windows) for t, windows in trainers_windows.items()}

    solution = {}
    unscheduled = []

    # Zoradíme páry podľa počtu dostupných slotov (najťažší prvý)
    def count_available(couple):
        return sum(1 for _, a in cawt.get(couple.name, []) if a)

    couples_sorted = sorted(couples, key=count_available)

    for couple in couples_sorted:
        placed = False
        duration = couple.min_duration
        needed_slots = (duration + 29) // 30  # 30-min sloty

        couple_avail = cawt.get(couple.name, [])
        if not couple_avail:
            unscheduled.append(couple)
            continue

        # Prejdeme všetkých trénerov
        for trainer, windows in trainer_slots.items():

            # Prejdeme všetky možné začiatky
            for i in range(len(windows) - needed_slots + 1):

                # Skontrolujeme trénera
                trainer_ok = all(windows[j][1] for j in range(i, i + needed_slots))
                if not trainer_ok:
                    continue

                # Skontrolujeme pár
                times_ok = True
                for j in range(i, i + needed_slots):
                    t_str = windows[j][0]
                    # nájdeme dostupnosť páru v tomto čase
                    match = next((a for ts, a in couple_avail if ts == t_str), None)
                    if match is None or match is False:
                        times_ok = False
                        break

                if not times_ok:
                    continue

                # Ak sme sa sem dostali → môžeme umiestniť
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
    return schedule_g if schedule_g else None, diag_g
