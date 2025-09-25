from App.models.staff import Staff
from App.models.shift import Shift
from App.models.timeentry import TimeEntry
from App.database import db
from datetime import datetime
from flask_login import current_user
from flask import abort 

# -------- LOGIN --------
def login(username, password):
    user = Staff.query.filter_by(username=username).first()
    if user and user.check_password(password):
        return user
    return None

# -------- SCHEDULE SHIFT (ADMIN) --------
def schedule_shift(admin_user, staff_user, date_str, start_str, end_str):
    if admin_user.role != "Admin":
        raise PermissionError("Only Admins can schedule shifts.")
    
    date = datetime.strptime(date_str, "%Y-%m-%d").date()
    start_time = datetime.strptime(start_str, "%H:%M").time()
    end_time = datetime.strptime(end_str, "%H:%M").time()
    
    shift = Shift(staff_id=staff_user.user_id, date=date, start_time=start_time, end_time=end_time)
    db.session.add(shift)
    db.session.commit()
    return shift

# -------- VIEW ROSTER (STAFF) --------
def view_roster(user):
    if user.role != "Staff":
        raise PermissionError("Access denied: Staff only.")
    
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


# -------- TIME IN / TIME OUT (STAFF) --------
def time_in(staff_user, shift_id):
    shift = Shift.query.get(shift_id)
    if not shift or shift.staff_id != staff_user.user_id:
        raise ValueError("Shift not found or not yours.")
    
    entry = TimeEntry(shift_id=shift_id, time_in=datetime.now().time())
    db.session.add(entry)
    db.session.commit()
    return entry

def time_out(staff_user, shift_id):
    entry = TimeEntry.query.filter_by(shift_id=shift_id).order_by(TimeEntry.id.desc()).first()
    if not entry:
        raise ValueError("No time in record found for this shift.")
    
    entry.time_out = datetime.now().time()
    db.session.commit()
    return entry

# -------- VIEW SHIFT REPORT (ADMIN) --------
def view_shift_report(admin_user):
    if admin_user.role != "Admin":
        raise PermissionError("Only Admins can view reports.")
    
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
