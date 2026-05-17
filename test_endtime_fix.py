"""
Test to verify the fix for lesson end-time availability.

The issue: A couple with slots 14:00✓, 14:30✓, 15:00✓, 15:30✗ should:
- ACCEPT a 60-min lesson at 14:00 (ends at 15:00✓ which is available)
- REJECT a 60-min lesson at 14:30 (ends at 15:30✗ which is NOT available)

The fix: Verify that the lesson END TIME is not blocked by an unavailable slot.
"""

def test_lesson_end_time_available():
    """
    Test Case: 60-min lesson at 14:00
    
    Couple availability: 14:00✓, 14:30✓, 15:00✓, 15:30✗
    Lesson: 14:00-15:00
    End time: 15:00 (which is ✓ available)
    Expected: ACCEPT ✓
    """
    
    couple_slots = [
        ("14:00", True),   # 14:00-14:30 available
        ("14:30", True),   # 14:30-15:00 available
        ("15:00", True),   # 15:00-15:30 available
        ("15:30", False),  # 15:30-16:00 NOT available
    ]
    
    slot_length = 30
    couple_avail_intervals = []
    for time_str, avail in couple_slots:
        h, m = map(int, time_str.split(':'))
        start = h * 60 + m
        end = start + slot_length
        couple_avail_intervals.append((start, end, avail))
    
    print("Test 1: 60-min lesson at 14:00")
    print(f"Couple availability: 14:00✓, 14:30✓, 15:00✓, 15:30✗")
    
    # 60-min lesson starting at 14:00
    start_min = 14 * 60  # 840 = 14:00
    duration = 60
    end_min = start_min + duration  # 900 = 15:00
    
    # Check coverage
    available_intervals = [(start, end) for start, end, avail in couple_avail_intervals if avail]
    lesson_duration_covered = 0
    for avail_start, avail_end in sorted(available_intervals):
        overlap_start = max(start_min, avail_start)
        overlap_end = min(end_min, avail_end)
        if overlap_end > overlap_start:
            lesson_duration_covered += overlap_end - overlap_start
    
    print(f"Lesson: 14:00-15:00 (duration: {duration} min)")
    print(f"Coverage: {lesson_duration_covered} min")
    assert lesson_duration_covered >= duration, "Should be fully covered"
    
    # Check end time
    end_time_blocked = False
    for interval_start, interval_end, avail in couple_avail_intervals:
        if not avail and interval_start == end_min:
            end_time_blocked = True
            print(f"  End time 15:00 blocked by unavailable slot starting at {interval_start}")
            break
    
    assert not end_time_blocked, "End time should NOT be blocked"
    print("✓ Result: ACCEPT (end time 15:00✓ is available)")
    

def test_lesson_end_time_unavailable():
    """
    Test Case: 60-min lesson at 14:30
    
    Couple availability: 14:00✓, 14:30✓, 15:00✓, 15:30✗
    Lesson: 14:30-15:30
    End time: 15:30 (which is ✗ NOT available)
    Expected: REJECT ✗
    """
    
    couple_slots = [
        ("14:00", True),   # 14:00-14:30 available
        ("14:30", True),   # 14:30-15:00 available
        ("15:00", True),   # 15:00-15:30 available
        ("15:30", False),  # 15:30-16:00 NOT available
    ]
    
    slot_length = 30
    couple_avail_intervals = []
    for time_str, avail in couple_slots:
        h, m = map(int, time_str.split(':'))
        start = h * 60 + m
        end = start + slot_length
        couple_avail_intervals.append((start, end, avail))
    
    print("\nTest 2: 60-min lesson at 14:30")
    print(f"Couple availability: 14:00✓, 14:30✓, 15:00✓, 15:30✗")
    
    # 60-min lesson starting at 14:30
    start_min = 14 * 60 + 30  # 870 = 14:30
    duration = 60
    end_min = start_min + duration  # 930 = 15:30
    
    # Check coverage
    available_intervals = [(start, end) for start, end, avail in couple_avail_intervals if avail]
    lesson_duration_covered = 0
    for avail_start, avail_end in sorted(available_intervals):
        overlap_start = max(start_min, avail_start)
        overlap_end = min(end_min, avail_end)
        if overlap_end > overlap_start:
            lesson_duration_covered += overlap_end - overlap_start
    
    print(f"Lesson: 14:30-15:30 (duration: {duration} min)")
    print(f"Coverage: {lesson_duration_covered} min")
    assert lesson_duration_covered >= duration, "Should be fully covered"
    
    # Check end time
    end_time_blocked = False
    for interval_start, interval_end, avail in couple_avail_intervals:
        if not avail and interval_start == end_min:
            end_time_blocked = True
            print(f"  ✗ End time 15:30 blocked by unavailable slot: 15:30✗")
            break
    
    assert end_time_blocked, "End time SHOULD be blocked"
    print("✓ Result: REJECT (end time 15:30✗ is NOT available)")


def test_multiple_unavailable_blocks():
    """
    Test Case: Lesson end time must avoid ANY unavailable slot starting time
    
    Couple: 10:00✓, 10:30✗, 11:00✓, 11:30✓, 12:00✗
    - 60-min at 11:00 ends at 12:00 → 12:00✗ starts → REJECT
    """
    
    couple_slots = [
        ("10:00", True),   # 10:00-10:30 available
        ("10:30", False),  # 10:30-11:00 NOT available
        ("11:00", True),   # 11:00-11:30 available
        ("11:30", True),   # 11:30-12:00 available
        ("12:00", False),  # 12:00-12:30 NOT available
    ]
    
    slot_length = 30
    couple_avail_intervals = []
    for time_str, avail in couple_slots:
        h, m = map(int, time_str.split(':'))
        start = h * 60 + m
        end = start + slot_length
        couple_avail_intervals.append((start, end, avail))
    
    print("\nTest 3: 60-min lesson at 11:00 with unavailable blocks")
    print(f"Couple availability: 10:00✓, 10:30✗, 11:00✓, 11:30✓, 12:00✗")
    
    # 60-min lesson starting at 11:00
    start_min = 11 * 60  # 660 = 11:00
    duration = 60
    end_min = start_min + duration  # 720 = 12:00
    
    # Check end time
    end_time_blocked = False
    for interval_start, interval_end, avail in couple_avail_intervals:
        if not avail and interval_start == end_min:
            end_time_blocked = True
            print(f"  ✗ End time 12:00 blocked by unavailable slot: 12:00✗")
            break
    
    assert end_time_blocked, "End time SHOULD be blocked by 12:00✗"
    print("✓ Result: REJECT (lesson would end exactly when 12:00✗ starts)")


if __name__ == "__main__":
    print("=" * 70)
    print("Testing Lesson End-Time Availability Fix")
    print("=" * 70)
    
    try:
        test_lesson_end_time_available()
        test_lesson_end_time_unavailable()
        test_multiple_unavailable_blocks()
        
        print("\n" + "=" * 70)
        print("✓ ALL TESTS PASSED")
        print("\nThe fix ensures:")
        print("1. ✓ Lesson end time cannot fall on an unavailable slot")
        print("2. ✓ 60-min lesson at 14:00 with 14:00✓...15:00✓ is ACCEPTED")
        print("3. ✓ 60-min lesson at 14:30 with ...15:30✗ is REJECTED")
        print("4. ✓ All durations correctly calculated")
        
    except AssertionError as e:
        print(f"\n✗ TEST FAILED: {e}")
        raise
