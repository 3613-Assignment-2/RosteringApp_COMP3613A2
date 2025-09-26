from App.models.staff import Staff
from App.models.shift import Shift
from App.models.timeentry import TimeEntry
from App.database import db
from datetime import datetime

def login(username, password):
    """Return the Staff object if username/password are valid."""
    user = Staff.query.filter_by(username=username).first()
    if user and user.check_password(password):
        return user
    return None

def schedule_shift(admin, staff, date_str, start_str, end_str):
    if admin.role != "Admin":
        print("Only Admins can schedule shifts.")
        return None
    
    date = datetime.strptime(date_str, "%d-%m-%Y").date()
    start_time = datetime.strptime(start_str, "%H:%M").time()
    end_time = datetime.strptime(end_str, "%H:%M").time()
    
    shift = Shift(staff_id=staff.user_id, date=date, start_time=start_time, end_time=end_time)
    db.session.add(shift)
    db.session.commit()
    return shift

def view_roster(user):
    if user.role != "Staff":
        print("Only Staff can view the roster.")
        return
    
    shifts = Shift.query.all()
    roster = []
    for s in shifts:
        roster.append({
            'shift_id': s.shift_id,
            'staff': s.staff.username,
            'date': s.date,
            'start': s.start_time,
            'end': s.end_time
        })
    return roster

def time_in(staff, shift_id):
    shift = Shift.query.get(shift_id)
    if not shift or shift.staff_id != staff.user_id:
        print("Shift not found or not yours.")
        return None
    
    entry = TimeEntry(shift_id=shift_id, time_in=datetime.now().time())
    db.session.add(entry)
    db.session.commit()
    return entry

def time_out(staff, shift_id):
    shift = Shift.query.get(shift_id)
    if not shift or shift.staff_id != staff.user_id:
        print("Shift not found or not yours.")
        return None
    
    entry = TimeEntry.query.filter_by(shift_id=shift_id).order_by(TimeEntry.id.desc()).first()
    if not entry:
        print("No time in record found for this shift.")
        return None
    
    entry.time_out = datetime.now().time()
    db.session.commit()
    return entry

def view_shift_report(admin):
    if admin.role != "Admin":
        print("Only Admins can view reports.")
        return []
    
    shifts = Shift.query.all()
    report = []
    for s in shifts:
        entries = TimeEntry.query.filter_by(shift_id=s.shift_id).all()
        report.append({
            'staff': s.staff.username,
            'date': s.date,
            'start': s.start_time,
            'end': s.end_time,
            'time_entries': [{'in': e.time_in, 'out': e.time_out} for e in entries]
        })
    return report

 
def change_password(username, old_password, new_password):
    user = Staff.query.filter_by(username=username).first()
    if not user:
        print("User not found.")
        return False
    
    if not user.check_password(old_password):
        print("Current password incorrect.")
        return False
    
    user.set_password(new_password)
    db.session.commit()
    print(f"Password for {username} updated successfully.")
    return True