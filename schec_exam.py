import argparse
import os
import random
import math
import time
import copy
from collections import defaultdict, Counter
import pandas as pd

random.seed(12345)

def detect_columns(df):
    """Optimized column detection with early returns"""
    cols = list(df.columns)
    lower = [c.lower() for c in cols]
    col_map = {}
    
    # Single pass through columns
    for idx, c in enumerate(lower):
        if "roll" in c and "no" in c:
            col_map["student"] = cols[idx]
        elif "code" in c or ("course" in c and "code" in c):
            col_map["course"] = cols[idx]
        elif "section" in c:
            col_map["section"] = cols[idx]
        elif "subject" in c and "name" in c:
            col_map["name"] = cols[idx]
    
    # Default assignments
    if "student" not in col_map:
        col_map["student"] = cols[0]
    if "course" not in col_map:
        col_map["course"] = cols[1] if len(cols) > 1 else cols[0]
    if "name" not in col_map:
        col_map["name"] = cols[-1]
        
    return col_map

def longest_run(indices):
    """Optimized longest consecutive run calculation"""
    if not indices: 
        return 0
    indices = sorted(set(indices))
    
    max_run = current_run = 1
    for i in range(1, len(indices)):
        if indices[i] == indices[i-1] + 1:
            current_run += 1
            max_run = max(max_run, current_run)
        else:
            current_run = 1
    return max_run

def build_maps(df, col_map):
    """Optimized data structure building"""
    student_col = col_map["student"]
    course_col = col_map["course"]
    name_col = col_map["name"]
    sec_col = col_map.get("section", None)
    
    course_students = defaultdict(set)
    student_courses = defaultdict(set)
    course_name = {}
    
    # Use vectorized operations where possible
    for _, r in df.iterrows():
        sid = str(r[student_col]).strip()
        code = str(r[course_col]).strip()
        
        if sec_col and sec_col in r:
            sec = str(r[sec_col]).strip()
            cid = f"{code} | {sec}"
        else:
            cid = code
            
        cname = str(r[name_col]) if name_col in r.index else ""
        
        course_students[cid].add(sid)
        student_courses[sid].add(cid)
        course_name[cid] = cname
        
    return course_students, student_courses, course_name

def initial_schedule(course_students, slot_list, slot_day, slot_index, CAP):
    """Optimized initial scheduling with better heuristics"""
    slot_courses = {sid: set() for sid in slot_list}
    slot_load = {sid: 0 for sid in slot_list}
    course_assignment = {}
    student_assigned_slots = defaultdict(list)
    
    # Precompute enrollments and sort
    course_enrollments = {c: len(students) for c, students in course_students.items()}
    courses_sorted = sorted(course_students.keys(), 
                          key=lambda c: course_enrollments[c], 
                          reverse=True)
    
    # Precompute day mappings
    day_slots = defaultdict(list)
    for sid in slot_list:
        day_slots[slot_day[sid]].append(sid)
    
    for c in courses_sorted:
        enroll = course_enrollments[c]
        best_slot = None
        best_score = float('inf')
        
        # Try slots in order of least loaded first
        for sid in sorted(slot_list, key=lambda s: slot_load[s]):
            # Quick capacity check
            if slot_load[sid] + enroll > CAP:
                continue
                
            # Check conflicts efficiently
            if any(sid in student_assigned_slots[st] for st in course_students[c]):
                continue
            
            # Calculate penalty score
            day = slot_day[sid]
            added_3plus = 0
            added_consec = 0
            
            for st in course_students[c]:
                # Count same-day courses
                same_day_count = sum(1 for s in student_assigned_slots[st] if slot_day[s] == day)
                if same_day_count >= 2:  # Penalize even at 2 courses
                    added_3plus += (same_day_count - 1) ** 2
                
                # Check consecutive runs
                if student_assigned_slots[st]:
                    day_indices = [slot_index[s] for s in student_assigned_slots[st] if slot_day[s] == day]
                    if day_indices:
                        current_run = longest_run(day_indices)
                        new_run = longest_run(day_indices + [slot_index[sid]])
                        if new_run > current_run:
                            added_consec += (new_run - current_run) ** 2
            
            # Aggressive scoring to minimize overloads
            score = (added_3plus * 5000 + 
                    added_consec * 1000 + 
                    (slot_load[sid] + enroll) / CAP * 100)
            
            if score < best_score:
                best_score = score
                best_slot = sid
        
        # Assign course
        if best_slot is not None:
            course_assignment[c] = best_slot
            slot_courses[best_slot].add(c)
            slot_load[best_slot] += enroll
            for st in course_students[c]:
                student_assigned_slots[st].append(best_slot)
        else:
            # Fallback assignment
            for sid in sorted(slot_list, key=lambda s: slot_load[s]):
                if not any(sid in student_assigned_slots[st] for st in course_students[c]):
                    if slot_load[sid] + enroll <= CAP + 50:
                        course_assignment[c] = sid
                        slot_courses[sid].add(c)
                        slot_load[sid] += enroll
                        for st in course_students[c]:
                            student_assigned_slots[st].append(sid)
                        break
    
    return course_assignment, slot_courses, slot_load, student_assigned_slots

def compute_metrics(student_assigned_slots, slot_day, slot_index):
    """Optimized metrics computation"""
    c3 = 0
    consec_count = 0
    
    for st, slots in student_assigned_slots.items():
        by_day = defaultdict(list)
        for sid in slots:
            by_day[slot_day[sid]].append(slot_index[sid])
        
        # Count students with 3+ exams per day
        for day_slots in by_day.values():
            if len(day_slots) >= 3:
                c3 += 1
        
        # Count consecutive exams
        for day_slots in by_day.values():
            if len(day_slots) >= 2:
                mr = longest_run(sorted(day_slots))
                if mr >= 3:
                    consec_count += 1
    
    return c3, consec_count

def optimized_simulated_annealing(course_students, student_courses, course_name,
                                 course_assignment, slot_courses, slot_load, 
                                 student_assigned_slots, slot_list, slot_day, 
                                 slot_index, CAP, time_limit=55, max_iters=3000):
    """Highly optimized simulated annealing with focus on reducing overloads"""
    
    # Precompute frequently used data
    course_enrollments = {c: len(students) for c, students in course_students.items()}
    course_student_list = {c: list(students) for c, students in course_students.items()}
    
    # Initialize best solution
    best_assignment = copy.deepcopy(course_assignment)
    best_slot_courses = copy.deepcopy(slot_courses)
    best_slot_load = copy.deepcopy(slot_load)
    best_student_slots = copy.deepcopy(student_assigned_slots)
    
    # Track students with overloads for targeted optimization
    def get_overloaded_students(student_slots):
        overloaded = set()
        for st, slots in student_slots.items():
            day_counts = defaultdict(int)
            for sid in slots:
                day_counts[slot_day[sid]] += 1
            if any(count >= 3 for count in day_counts.values()):
                overloaded.add(st)
        return overloaded
    
    # Fast delta computation
    def compute_move_delta(c, s_from, s_to, student_slots, slot_load_local):
        enroll = course_enrollments[c]
        
        # Quick feasibility checks
        if slot_load_local[s_to] + enroll > CAP:
            return float('inf')
        
        # Check conflicts
        for st in course_student_list[c]:
            if s_to in student_slots[st]:
                return float('inf')
        
        # Compute actual delta
        day_from, day_to = slot_day[s_from], slot_day[s_to]
        idx_from, idx_to = slot_index[s_from], slot_index[s_to]
        
        delta_score = 0
        
        for st in course_student_list[c]:
            # Same-day count changes
            from_count_before = sum(1 for s in student_slots[st] if slot_day[s] == day_from)
            to_count_before = sum(1 for s in student_slots[st] if slot_day[s] == day_to)
            
            from_count_after = from_count_before - 1
            to_count_after = to_count_before + 1
            
            # Heavy penalties for overloads
            if from_count_before >= 3 and from_count_after < 3:
                delta_score -= 10000
            elif from_count_before < 3 and from_count_after >= 3:
                delta_score += 10000
                
            if to_count_before >= 3 and to_count_after < 3:
                delta_score -= 10000
            elif to_count_before < 3 and to_count_after >= 3:
                delta_score += 10000
            
            # Consecutive run penalties
            def get_day_indices(st, day):
                return [slot_index[s] for s in student_slots[st] if slot_day[s] == day]
            
            from_indices_before = get_day_indices(st, day_from)
            from_indices_after = [i for i in from_indices_before if i != idx_from]
            to_indices_before = get_day_indices(st, day_to)
            to_indices_after = to_indices_before + [idx_to]
            
            from_run_before = longest_run(sorted(from_indices_before)) if from_indices_before else 0
            from_run_after = longest_run(sorted(from_indices_after)) if from_indices_after else 0
            to_run_before = longest_run(sorted(to_indices_before)) if to_indices_before else 0
            to_run_after = longest_run(sorted(to_indices_after))
            
            # Aggressive consecutive penalties
            if from_run_after >= 3:
                delta_score += 500 * from_run_after
            if to_run_after >= 3:
                delta_score += 500 * to_run_after
            if from_run_before >= 3:
                delta_score -= 500 * from_run_before
            if to_run_before >= 3:
                delta_score -= 500 * to_run_before
        
        return delta_score
    
    # Main optimization loop
    start_time = time.time()
    temperature = 1.0
    min_temperature = 0.001
    decay_rate = (min_temperature / 1.0) ** (1.0 / max_iters)
    
    for iteration in range(max_iters):
        if time.time() - start_time > time_limit:
            break
            
        temperature *= decay_rate
        
        # Focus on overloaded students 80% of the time
        if random.random() < 0.8:
            overloaded = get_overloaded_students(best_student_slots)
            if not overloaded:
                # If no overloads, try to reduce consecutive exams
                all_students = list(best_student_slots.keys())
                if not all_students:
                    continue
                st = random.choice(all_students)
                candidate_courses = list(student_courses.get(st, []))
            else:
                st = random.choice(list(overloaded))
                candidate_courses = list(student_courses.get(st, []))
        else:
            candidate_courses = list(course_students.keys())
        
        if not candidate_courses:
            continue
            
        c = random.choice(candidate_courses)
        s_from = best_assignment.get(c)
        if s_from is None:
            continue
            
        # Try moves to reduce overloads
        improved = False
        for s_to in random.sample(slot_list, min(10, len(slot_list))):
            if s_to == s_from:
                continue
                
            delta = compute_move_delta(c, s_from, s_to, best_student_slots, best_slot_load)
            
            if delta < 0 or (delta < 1000 and random.random() < math.exp(-delta / (temperature + 1e-12))):
                # Apply move
                best_assignment[c] = s_to
                best_slot_courses[s_from].remove(c)
                best_slot_courses[s_to].add(c)
                
                enroll = course_enrollments[c]
                best_slot_load[s_from] -= enroll
                best_slot_load[s_to] += enroll
                
                for st in course_student_list[c]:
                    best_student_slots[st].remove(s_from)
                    best_student_slots[st].append(s_to)
                
                improved = True
                break
        
        # Occasionally try swaps
        if not improved and iteration % 20 == 0:
            c1, c2 = random.sample(list(course_students.keys()), 2)
            s1, s2 = best_assignment.get(c1), best_assignment.get(c2)
            if s1 and s2 and s1 != s2:
                # Quick conflict check
                conflict = (any(s2 in best_student_slots[st] for st in course_students[c1] if st not in course_students[c2]) or
                          any(s1 in best_student_slots[st] for st in course_students[c2] if st not in course_students[c1]))
                
                if not conflict:
                    # Temporary swap to evaluate
                    best_assignment[c1], best_assignment[c2] = s2, s1
                    best_slot_courses[s1].remove(c1); best_slot_courses[s2].add(c1)
                    best_slot_courses[s2].remove(c2); best_slot_courses[s1].add(c2)
                    
                    for st in course_students[c1]:
                        best_student_slots[st].remove(s1)
                        best_student_slots[st].append(s2)
                    for st in course_students[c2]:
                        best_student_slots[st].remove(s2)
                        best_student_slots[st].append(s1)
    
    final_c3, final_consec_count = compute_metrics(best_student_slots, slot_day, slot_index)
    return best_assignment, best_slot_courses, best_slot_load, best_student_slots, final_c3, final_consec_count

def write_outputs(outdir, assignment, slot_courses, course_name, course_students, slot_day, slot_index):
    """Optimized output writing"""
    os.makedirs(outdir, exist_ok=True)
    
    rows = []
    for c, sid in assignment.items():
        if sid:  # Only include assigned courses
            rows.append({
                "course_id": c,
                "subject_name": course_name.get(c, ""),
                "slot_id": sid,
                "day": slot_day[sid],
                "slot_no": slot_index[sid],
                "enrollment": len(course_students[c])
            })
    
    df = pd.DataFrame(rows).sort_values(["day", "slot_no"])
    sched_csv = os.path.join(outdir, "schedule_final_optimized.csv")
    df.to_csv(sched_csv, index=False)
    return sched_csv

def write_report(outdir, student_slots, slot_courses, course_students, slot_day, slot_index, initial_c3, final_c3, initial_consec, final_consec):
    """Comprehensive reporting"""
    report_lines = []
    report_lines.append("Final Optimized Scheduling Report\n")
    report_lines.append("=" * 50 + "\n\n")
    
    report_lines.append(f"Initial students with 3+ exams/day: {initial_c3}\n")
    report_lines.append(f"Final students with 3+ exams/day: {final_c3}\n")
    report_lines.append(f"Improvement: {initial_c3 - final_c3} students\n\n")
    
    report_lines.append(f"Initial students with 3+ consecutive exams: {initial_consec}\n")
    report_lines.append(f"Final students with 3+ consecutive exams: {final_consec}\n")
    report_lines.append(f"Improvement: {initial_consec - final_consec} students\n\n")
    
    # Slot utilization
    report_lines.append("Slot Utilization:\n")
    report_lines.append("-" * 20 + "\n")
    for sid in sorted(slot_courses.keys(), key=lambda s: (slot_day[s], slot_index[s])):
        total_students = sum(len(course_students[c]) for c in slot_courses[sid])
        unique_students = len(set().union(*(course_students[c] for c in slot_courses[sid])))
        report_lines.append(f"{sid}: {unique_students} unique students, {total_students} total seats\n")
    
    # Same-day distribution
    day_distribution = Counter()
    for st, slots in student_slots.items():
        day_counts = Counter(slot_day[sid] for sid in slots)
        for count in day_counts.values():
            if count >= 3:
                day_distribution[count] += 1
    
    report_lines.append("\nSame-Day Exam Distribution:\n")
    report_lines.append("-" * 30 + "\n")
    for count in [3, 4, 5, 6]:
        report_lines.append(f"Students with {count} exams/day: {day_distribution[count]}\n")
    
    # Consecutive distribution
    consec_distribution = Counter()
    for st, slots in student_slots.items():
        by_day = defaultdict(list)
        for sid in slots:
            by_day[slot_day[sid]].append(slot_index[sid])
        for day_slots in by_day.values():
            run_length = longest_run(sorted(day_slots))
            if run_length >= 3:
                consec_distribution[run_length] += 1
    
    report_lines.append("\nConsecutive Exams Distribution:\n")
    report_lines.append("-" * 35 + "\n")
    for length in [3, 4, 5, 6]:
        report_lines.append(f"Students with {length} consecutive exams: {consec_distribution[length]}\n")
    
    # Write report
    report_path = os.path.join(outdir, "schedule_report_final.txt")
    with open(report_path, "w") as f:
        f.writelines(report_lines)
    
    return report_path

def main():
    parser = argparse.ArgumentParser(description="Optimized Exam Scheduler")
    parser.add_argument("--input", "-i", required=True, help="Input Excel file path")
    parser.add_argument("--outdir", "-o", default="./final_output", help="Output directory")
    parser.add_argument("--capacity", "-c", type=int, default=500, help="Maximum students per slot")
    args = parser.parse_args()

    # Load and process data
    print("Loading data...")
    df = pd.read_excel(args.input)
    col_map = detect_columns(df)
    course_students, student_courses, course_name = build_maps(df, col_map)
    
    print(f"Processed {len(course_students)} courses and {len(student_courses)} students")

    # Setup slots
    DAYS, SLOTS_PER_DAY = 3, 6
    slot_list = [f"D{d}_S{s}" for d in range(1, DAYS+1) for s in range(1, SLOTS_PER_DAY+1)]
    slot_day = {sid: int(sid.split("_S")[0][1:]) for sid in slot_list}
    slot_index = {sid: int(sid.split("_S")[1]) for sid in slot_list}

    # Initial scheduling
    print("Running initial scheduling...")
    start_time = time.time()
    course_assignment, slot_courses, slot_load, student_assigned_slots = initial_schedule(
        course_students, slot_list, slot_day, slot_index, args.capacity
    )
    initial_c3, initial_consec_count = compute_metrics(student_assigned_slots, slot_day, slot_index)
    print(f"Initial schedule completed in {time.time() - start_time:.2f}s")
    print(f"Initial metrics - 3+ exams/day: {initial_c3}, 3+ consecutive: {initial_consec_count}")

    # Optimization
    print("Running optimization...")
    start_time = time.time()
    best_assignment, best_slot_courses, best_slot_load, best_student_slots, final_c3, final_consec_count = optimized_simulated_annealing(
        course_students, student_courses, course_name, course_assignment, 
        slot_courses, slot_load, student_assigned_slots, slot_list, 
        slot_day, slot_index, args.capacity, time_limit=55, max_iters=3000
    )
    print(f"Optimization completed in {time.time() - start_time:.2f}s")

    # Output results
    sched_csv = write_outputs(args.outdir, best_assignment, best_slot_courses, course_name, course_students, slot_day, slot_index)
    report_path = write_report(args.outdir, best_student_slots, best_slot_courses, course_students, slot_day, slot_index, initial_c3, final_c3, initial_consec_count, final_consec_count)

    print("\n" + "="*60)
    print("OPTIMIZATION COMPLETED SUCCESSFULLY!")
    print("="*60)
    print(f"Schedule saved: {sched_csv}")
    print(f"Report saved: {report_path}")
    print(f"\nFinal Results:")
    print(f"Students with 3+ exams/day: {final_c3} (was {initial_c3})")
    print(f"Students with 3+ consecutive exams: {final_consec_count} (was {initial_consec_count})")

if __name__ == "__main__":
    main()