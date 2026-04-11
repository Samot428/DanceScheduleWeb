# Schedule Algorithm Validation Report

## Summary
The schedule-making algorithm has **TWO CRITICAL BUGS**:
1. **Missing slot duration calculation** in `backtracking_schedule` (LINE 77)
2. **Incorrect interval calculation** in `compute_couple_options` (LINES 44-45, 58)

---

## The Issue: Inconsistent Slot Calculation

### Example Scenario
- Couple available: 20:00 = ✓ True, 20:30 = ✗ False
- Lesson duration: 60 minutes (requires both 20:00-20:30 AND 20:30-21:00)
- **Expected:** Couple should NOT be scheduled (fails at 20:30 slot)

### The Bug

#### In `backtracking_schedule()` [making_schedule_func2.py, line ~23]:
```python
needed_slots = (duration + 4) // 5
# For a 60-minute lesson: (60 + 4) // 5 = 64 // 5 = 12 slots
```

#### In `greedy_schedule()` [making_schedule_func2.py, line ~141]:
```python
needed_slots = (duration + 29) // 30
# For a 60-minute lesson: (60 + 29) // 30 = 89 // 30 = 2 slots
```

### Root Cause
Both functions create trainer time windows with **30-minute intervals** (from [making_schedule_func2.py](making_schedule_func2.py#L18)):
```python
for i in range(st, et, 30):  # 30-minute slots!
    time_windows.append((time_str, is_available))
```

**But the formulas assume different slot durations!**
- `backtracking`: Assumes 5-minute slots (dividing by 5)
- `greedy`: Correctly assumes 30-minute slots (dividing by 30)

---

## Impact

### ✅ Correct Behavior (greedy_schedule)
- 60-min lesson = 2 slots × 30 min = 60 min ✓
- Correctly validates couple availability for ALL 2 slots

### ❌ Incorrect Behavior (backtracking_schedule)
- 60-min lesson = 12 slots × 5 min = 60 min (but slots are 30 min!)
- This formula would:
  - For a 60-min lesson: try to iterate 12 times through only 2 actual slots
  - Likely cause an index error OR skip availability checks
  - May place couples even when they're unavailable at some intervals

---

## Code Locations

| Function | File | Line | Issue |
|----------|------|------|-------|
| `backtracking_schedule()` | [making_schedule_func2.py](making_schedule_func2.py#L76) | ~76-77 | Wrong slot calculation |
| `greedy_schedule()` | [making_schedule_func2.py](making_schedule_func2.py#L141) | ~141 | ✓ Correct |
| `make_trainers_windows()` | [making_schedule_func2.py](making_schedule_func2.py#L18) | ~18 | Creates 30-min slots |

---

## Validation: Checking Couple Availability Logic

### Both functions DO check full duration availability:

**backtracking_schedule - can_place():**
```python
for j in range(start_idx, start_idx + needed_slots):
    time_str, trainer_free = windows[j]
    
    # Check couple availability for EACH slot
    for t_str, is_avail in couple_avail:
        if t_str == time_str:
            if not is_avail:  # ✓ Rejects if ANY slot is False
                return False, []
```

**greedy_schedule:**
```python
times_ok = True
for j in range(i, i + needed_slots):
    t_str = windows[j][0]
    match = next((a for ts, a in couple_avail if ts == t_str), None)
    if match is None or match is False:  # ✓ Rejects if ANY slot is False
        times_ok = False
        break
```

✅ **The availability checking logic itself is correct** - both reject if ANY slot in the duration is unavailable.

### But the bug is in `needed_slots` calculation:
- If `needed_slots` is calculated wrong, the loop iterates the wrong number of times
- May never reach unavailable slots that should be checked

---

## Example: 60-Minute Lesson at 20:00

### Couple Availability (30-min granularity):
```
20:00 → True
20:30 → False  ← Couple unavailable! (This is the 20:30-21:00 slot)
```

### Trainer Windows (30-min slots):
```
Index 0: "20:00" (free)
Index 1: "20:30" (free)
```

### What SHOULD Happen:
- Lesson needs slots at indices 0 AND 1
- Should check BOTH "20:00" (✓) and "20:30" (✗)
- Should REJECT because couple unavailable at index 1

### With Backtracking Bug:
```python
needed_slots = (60 + 4) // 5 = 12
# Tries to check indices 0 through 11...
# But windows only has 2 elements (indices 0-1)
# This causes either:
# - Index out of bounds error, OR
# - Loop conditions prevent reaching past index 1
```

---

## Recommendations

### ✅ FIX 1: APPLIED - Corrected backtracking slot calculation
**File:** [making_schedule_func2.py](making_schedule_func2.py#L76-77)

**Changed:**
```python
# BEFORE (WRONG - 5 minute slots):
needed_slots = (duration + 4) // 5

# AFTER (CORRECT - 30 minute slots):
needed_slots = (duration + 29) // 30  # Fixed: Slots are 30 minutes, not 5
```

### ✅ FIX 2: APPLIED - Corrected compute_couple_options interval calculations
**File:** [making_schedule_func2.py](making_schedule_func2.py#L42-60)

**Changed Multiple Locations:**

Location 1 - Interval end calculation when couple becomes unavailable:
```python
# BEFORE (WRONG - only +5 minutes):
intervals.append((current_start, last_min + 5))

# AFTER (CORRECT - full +30 minute slot):
intervals.append((current_start, last_min + 30))  # Fixed: Add 30 minutes (full slot duration)
```

Location 2 - Interval end calculation at array end:
```python
# BEFORE (WRONG - only +5 minutes):
intervals.append((current_start, last_min + 5))

# AFTER (CORRECT - full +30 minute slot):
intervals.append((current_start, last_min + 30))  # Fixed: Add 30 minutes (full slot duration)
```

Location 3 - Possible start positions calculation:
```python
# BEFORE (WRONG - 5 minute increments):
total_options += max(1, (e - s - couple.min_duration) // 5 + 1)

# AFTER (CORRECT - 30 minute slots):
total_options += max(1, (e - s - couple.min_duration) // 30 + 1)  # Fixed: Use 30-minute intervals
```

---

## Validation

All fixes have been validated with comprehensive test cases:

✅ **test_couple_unavailable_at_duration_end()** - Confirms couples are correctly rejected when unavailable at ANY slot within lesson duration

✅ **test_compute_couple_options_fix()** - Confirms correct calculation of possible lesson positions

✅ **test_interval_end_calculation()** - Confirms intervals properly represent full 30-minute slot durations

**Test Status:** ALL PASS ✓

See [test_schedule_bug_fixes.py](test_schedule_bug_fixes.py) for full validation suite.

---

## Impact Summary

| Function | Bug | Impact | Status |
|----------|-----|--------|--------|
| `backtracking_schedule` | Wrong slot calculation (÷5 instead of ÷30) | Potential invalid scheduling | ✅ FIXED |
| `compute_couple_options` | Wrong interval ends (+5 instead of +30) | Miscounts available options | ✅ FIXED |
| `compute_couple_options` | Wrong granularity for start positions (÷5) | Inflates possible positions | ✅ FIXED |
| `greedy_schedule` | None | Uses correct calculations | ✓ OK |
| Couple availability checking | None | Logic is sound | ✓ OK |

---

## How It Works Now (After Fixes)

### Example: 20:00 = True, 20:30 = False, 60-minute lesson

**Before Schedule Algorithm Runs:**
```
Trainer windows: [(20:00, True), (20:30, True), (21:00, True)]
Couple availability: [(20:00, True), (20:30, False), (21:00, True)]
```

**backtracking_schedule - can_place() function:**
```
couple.min_duration = 60
needed_slots = (60 + 29) // 30 = 2 ✓ CORRECT

Loop through slots 0 to 1:
  Slot 0 (20:00): Trainer=True ✓, Couple=True ✓
  Slot 1 (20:30): Trainer=True ✓, Couple=False ✗
  
RESULT: Cannot place couple → returns False ✓ CORRECT
```

**Result:** ✗ REJECTED - Cannot schedule 60-min lesson at 20:00

---

## Affected Algorithm Path

**When is backtracking_schedule used?**

From [making_schedule_func2.py](making_schedule_func2.py#L230):
```python
# 2. Skús backtracking
schedule, diag_bt = backtracking_schedule(...)
```

It's the PRIMARY scheduling attempt. Only if it fails is the greedy fallback used.
This means:
- **Most schedules use the buggy backtracking function**
- Greedy fallback is only used as failover

---

## Testing Recommendations

1. Create test with couple having partial availability:
   ```
   20:00-21:00 = [True, False, False, True]  (30-min slots)
   Lesson durations: Try 30min, 60min, 90min
   Verify only valid placements accepted
   ```

2. Compare results between backtracking and greedy
   - They should produce identical results
   - If they differ, it indicates the bug

3. Log `needed_slots` calculation during scheduling
   - Should equal ceil(duration / 30)

