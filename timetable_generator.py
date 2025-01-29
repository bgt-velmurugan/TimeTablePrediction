import random
from collections import defaultdict
import heapq

def generate_timetable(department, classes_per_day, days_per_week, staff_subjects):
    timetable = []
    days = ['Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday', 'Saturday'][:days_per_week]
    
    # Initialize counters for balancing workload and summary
    staff_count = defaultdict(int)
    subject_count = defaultdict(int)
    staff_summary = defaultdict(lambda: {'classes': 0, 'hours': 0})

    # Create a list of staff members
    staff_list = list(set(staff for staff, _ in staff_subjects))
    
    # Create a priority queue for staff selection
    staff_queue = [(0, staff) for staff in staff_list]
    heapq.heapify(staff_queue)

    for day in days:
        daily_schedule = []
        available_subjects = defaultdict(list)
        
        # Populate available subjects for each staff
        for staff, subject in staff_subjects:
            available_subjects[staff].append(subject)
        
        for class_num in range(classes_per_day + 3):  # +3 for 2 breaks and 1 lunch
            if class_num == 2 or class_num == 6:
                # Add a 15-minute break after 2nd and 6th periods
                daily_schedule.append({
                    'subject': 'Break',
                    'teacher': '',
                    'duration': '15 minutes'
                })
            elif class_num == 4:
                # Add a 45-minute lunch after 4th period
                daily_schedule.append({
                    'subject': 'Lunch',
                    'teacher': '',
                    'duration': '45 minutes'
                })
            else:
                # Select staff with the least number of assigned classes
                classes_assigned, selected_staff = heapq.heappop(staff_queue)
                
                # Select a subject for the staff
                if available_subjects[selected_staff]:
                    subject = min(available_subjects[selected_staff], key=lambda s: subject_count[s])
                else:
                    # If no subjects available for this staff, choose randomly from all subjects
                    subject = random.choice([s for s, _ in staff_subjects])
                
                staff_count[selected_staff] += 1
                subject_count[subject] += 1
                staff_summary[selected_staff]['classes'] += 1
                staff_summary[selected_staff]['hours'] += 0.75  # 45 minutes = 0.75 hours

                daily_schedule.append({
                    'subject': subject,
                    'teacher': selected_staff,
                    'duration': '45 minutes'
                })
                
                # Update the priority queue
                heapq.heappush(staff_queue, (classes_assigned + 1, selected_staff))

        timetable.append({'day': day, 'schedule': daily_schedule})

    # Convert staff_summary to a list of dictionaries for easier rendering in the template
    staff_summary_list = [{'name': staff, 'classes': data['classes'], 'hours': data['hours']} 
                          for staff, data in staff_summary.items()]

    return timetable, staff_summary_list

def adjust_timetable(timetable, day, old_index, new_index):
    day_schedule = next(d for d in timetable if d['day'] == day)
    class_to_move = day_schedule['schedule'].pop(old_index)
    day_schedule['schedule'].insert(new_index, class_to_move)
    return timetable

