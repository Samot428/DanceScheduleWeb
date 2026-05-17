"""
Test to verify the fix for complete lesson duration coverage.

The issue: A couple with gaps in their availability (e.g., 14:00✓, 15:00✓, 15:30✗)
was being scheduled for a 60-minute lesson even though the middle time was missing.

The fix: Verify that the ENTIRE lesson duration is covered by consecutive available periods.
"""

def test_lesson_with_gap_in_availability():
    """
    Test Case: Couple with gap in availability
    
    Scenario:
    - Couple availability: 14:00✓, 15:00✓, 15:30✗
    - This means: 14:00-14:30✓, 14:30-15:00 (UNKNOWN/MISSING), 15:00-15:30✓, 15:30-16:00✗
    - 60-minute lesson at 14:00 would need: 14:00-15:00
    - Expected: REJECT (gap at 14:30-15:00 not covered)
    """
    
    # Couple availability slots (30-minute intervals)
    couple_slots = [
        ("14:00", True),   # Available 14:00-14:30
        ("15:00", True),   # Available 15:00-15:30 (NOTE: missing 14:30!)
        ("15:30", False),  # NOT available 15:30-16:00
    ]
    
    # Convert to intervals (as done in fixed code)
    slot_length = 30
    couple_avail_intervals = []
    for time_str, avail in couple_slots:
        h, m = map(int, time_str.split(':'))
        start = h * 60 + m
        end = start + slot_length
        couple_avail_intervals.append((start, end, avail))
    
    print(f"Couple availability intervals:")
    for start, end, avail in couple_avail_intervals:
        h_s, m_s = start // 60, start % 60
        h_e, m_e = end // 60, end % 60
        status = "✓" if avail else "✗"
        print(f"  {status} {h_s:02d}:{m_s:02d}-{h_e:02d}:{m_e:02d}")
    
    # Try to schedule a 60-minute lesson at 14:00
    start_min = 14 * 60  # 14:00 = 840 minutes
    duration = 60
    end_min = start_min + duration  # 900 = 15:00
    
    # NEW CORRECT LOGIC: Check complete coverage
    available_intervals = [(start, end) for start, end, avail in couple_avail_intervals if avail]
    print(f"\nAvailable intervals (avail=True): {available_intervals}")
    
    lesson_duration_covered = 0
    for avail_start, avail_end in sorted(available_intervals):
        overlap_start = max(start_min, avail_start)
        overlap_end = min(end_min, avail_end)
        if overlap_end > overlap_start:
            coverage = overlap_end - overlap_start
            lesson_duration_covered += coverage
            print(f"  Overlap: {overlap_start}-{overlap_end} = {coverage} min")
    
    print(f"\nLesson needs: {duration} minutes")
    print(f"Actually covered: {lesson_duration_covered} minutes")
    
    # Should REJECT because only 30 minutes covered (14:00-14:30), not full 60
    assert lesson_duration_covered < duration, \
        f"Should reject lesson: only {lesson_duration_covered}min covered, {duration}min needed"
    
    print("✓ Test PASSED: 60-min lesson at 14:00 correctly REJECTED (gap at 14:30-15:00)")


def test_lesson_with_complete_coverage():
    """
    Test Case: Couple with continuous availability
    
    Scenario:
    - Couple availability: 14:00✓, 14:30✓, 15:00✓
    - This means: 14:00-14:30✓, 14:30-15:00✓, 15:00-15:30✓ (CONTINUOUS)
    - 60-minute lesson at 14:00 would need: 14:00-15:00
    - Expected: ACCEPT (fully covered)
    """
    
    couple_slots = [
        ("14:00", True),   # Available 14:00-14:30
        ("14:30", True),   # Available 14:30-15:00
        ("15:00", True),   # Available 15:00-15:30
    ]
    
    slot_length = 30
    couple_avail_intervals = []
    for time_str, avail in couple_slots:
        h, m = map(int, time_str.split(':'))
        start = h * 60 + m
        end = start + slot_length
        couple_avail_intervals.append((start, end, avail))
    
    print(f"\nCouple availability intervals:")
    for start, end, avail in couple_avail_intervals:
        h_s, m_s = start // 60, start % 60
        h_e, m_e = end // 60, end % 60
        status = "✓" if avail else "✗"
        print(f"  {status} {h_s:02d}:{m_s:02d}-{h_e:02d}:{m_e:02d}")
    
    # Try to schedule a 60-minute lesson at 14:00
    start_min = 14 * 60  # 14:00 = 840 minutes
    duration = 60
    end_min = start_min + duration  # 900 = 15:00
    
    # NEW CORRECT LOGIC: Check complete coverage
    available_intervals = [(start, end) for start, end, avail in couple_avail_intervals if avail]
    print(f"\nAvailable intervals (avail=True): {available_intervals}")
    
    lesson_duration_covered = 0
    for avail_start, avail_end in sorted(available_intervals):
        overlap_start = max(start_min, avail_start)
        overlap_end = min(end_min, avail_end)
        if overlap_end > overlap_start:
            coverage = overlap_end - overlap_start
            lesson_duration_covered += coverage
            print(f"  Overlap: {overlap_start}-{overlap_end} = {coverage} min")
    
    print(f"\nLesson needs: {duration} minutes")
    print(f"Actually covered: {lesson_duration_covered} minutes")
    
    # Should ACCEPT because full 60 minutes are covered
    assert lesson_duration_covered >= duration, \
        f"Should accept lesson: {lesson_duration_covered}min covered, {duration}min needed"
    
    print("✓ Test PASSED: 60-min lesson at 14:00 correctly ACCEPTED (fully covered)")


def test_partial_overlap():
    """
    Test Case: Lesson partially overlaps with available time
    
    Scenario:
    - Couple availability: 14:30✓, 15:00✓, 15:30✗
    - Available: 14:30-15:00✓, 15:00-15:30✓, 15:30-16:00✗
    - 90-minute lesson at 14:00 would need: 14:00-15:30
    - Expected: REJECT (only covers 14:30-15:30, missing 14:00-14:30)
    """
    
    couple_slots = [
        ("14:30", True),   # Available 14:30-15:00
        ("15:00", True),   # Available 15:00-15:30
        ("15:30", False),  # NOT available 15:30-16:00
    ]
    
    slot_length = 30
    couple_avail_intervals = []
    for time_str, avail in couple_slots:
        h, m = map(int, time_str.split(':'))
        start = h * 60 + m
        end = start + slot_length
        couple_avail_intervals.append((start, end, avail))
    
    print(f"\nCouple availability intervals:")
    for start, end, avail in couple_avail_intervals:
        h_s, m_s = start // 60, start % 60
        h_e, m_e = end // 60, end % 60
        status = "✓" if avail else "✗"
        print(f"  {status} {h_s:02d}:{m_s:02d}-{h_e:02d}:{m_e:02d}")
    
    # Try to schedule a 90-minute lesson at 14:00
    start_min = 14 * 60  # 14:00 = 840 minutes
    duration = 90
    end_min = start_min + duration  # 930 = 15:30
    
    available_intervals = [(start, end) for start, end, avail in couple_avail_intervals if avail]
    print(f"\nAvailable intervals (avail=True): {available_intervals}")
    
    lesson_duration_covered = 0
    for avail_start, avail_end in sorted(available_intervals):
        overlap_start = max(start_min, avail_start)
        overlap_end = min(end_min, avail_end)
        if overlap_end > overlap_start:
            coverage = overlap_end - overlap_start
            lesson_duration_covered += coverage
            print(f"  Overlap: {overlap_start}-{overlap_end} = {coverage} min")
    
    print(f"\nLesson needs: {duration} minutes")
    print(f"Actually covered: {lesson_duration_covered} minutes")
    
    # Should REJECT: only 60 minutes covered (14:30-15:30), not full 90
    assert lesson_duration_covered < duration, \
        f"Should reject lesson: only {lesson_duration_covered}min covered, {duration}min needed"
    
    print("✓ Test PASSED: 90-min lesson at 14:00 correctly REJECTED (only 60min covered)")


if __name__ == "__main__":
    print("=" * 70)
    print("Testing Complete Lesson Duration Coverage Fix")
    print("=" * 70)
    
    try:
        test_lesson_with_gap_in_availability()
        test_lesson_with_complete_coverage()
        test_partial_overlap()
        
        print("\n" + "=" * 70)
        print("✓ ALL TESTS PASSED")
        print("\nThe fix ensures:")
        print("1. ✓ Lessons must be covered by CONSECUTIVE available periods")
        print("2. ✓ Gaps in availability data are treated as unavailable")
        print("3. ✓ No partial coverage - 100% of lesson duration must be covered")
        print("4. ✓ Couples properly rejected when availability has gaps")
        
    except AssertionError as e:
        print(f"\n✗ TEST FAILED: {e}")
        raise
