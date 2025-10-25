from App.models.staff import Staff
from App.models.shift import Shift
from App.models.timeentry import TimeEntry
from App.database import db
from datetime import date, datetime, timedelta

def authenticate(username, password):
    user = Staff.query.filter_by(username=username).first()
    if user and user.check_password(password):
        return user
    return None

def schedule_shift(admin, staff, date_str, start_str, end_str):
    if admin.role != "Admin":
        print("Only Admins can schedule shifts.")
        return None

    date = datetime.strptime(date_str, "%d-%m-%Y").date()
    today = date.today()
    start_of_week = today - timedelta(days=today.weekday())
    end_of_week = start_of_week + timedelta(days=6)

    if not (start_of_week <= date <= end_of_week):
        raise ValueError("Shifts can only be scheduled within the current week.")

    start_time = datetime.strptime(start_str, "%H:%M").time()
    end_time = datetime.strptime(end_str, "%H:%M").time()

    existing_shift = Shift.query.filter_by(
        staff_id=staff.user_id,
        date=date,
        start_time=start_time,
        end_time=end_time
    ).first()

    if existing_shift:
        raise ValueError("Shift already exists for this staff member at the same time.")

    shift = Shift(
        staff_id=staff.user_id,
        date=date,
        start_time=start_time,
        end_time=end_time
    )
    db.session.add(shift)
    db.session.commit()
    return shift


def view_roster(user):
    if not user or user.role != "Staff":
        print("Only Staff can view the roster.")
        return
    
    shifts = Shift.query.all()
    roster = []
    for s in shifts:
        roster.append({
            'shift_id': s.shift_id,
            'staff': s.staff.username,
            'date': s.date,
            'start': s.start_time.strftime("%H:%M:%S"),
            'end': s.end_time.strftime("%H:%M:%S")
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

    today = datetime.now().date()
    start_of_week = today - timedelta(days=today.weekday())
    end_of_week = start_of_week + timedelta(days=6)

    shifts = Shift.query.filter(Shift.date.between(start_of_week, end_of_week)).all()
    report = []
    for s in shifts:
        entry = TimeEntry.query.filter_by(shift_id=s.shift_id).order_by(TimeEntry.id.desc()).first()
        if entry:
            time_entry = {
                'in': entry.time_in.strftime("%H:%M:%S") if entry.time_in else None,
                'out': entry.time_out.strftime("%H:%M:%S") if entry.time_out else None
            }
        else:
            time_entry = {'in': None, 'out': None}

        report.append({
            'staff': s.staff.username,
            'date': s.date.strftime("%Y-%m-%d"),
            'start': s.start_time.strftime("%H:%M:%S"),
            'end': s.end_time.strftime("%H:%M:%S"),
            'time_entry': time_entry
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

def add_staff(admin, new_username, new_password):
    if admin.role != "Admin":
        print("Only Admins can add staff.")
        return None
    
    if Staff.query.filter_by(username=new_username).first():
        print("User already exists.")
        return None
    
    staff = Staff(username=new_username, password=new_password, role="Staff")
    db.session.add(staff)
    db.session.commit()
    print(f"User {new_username} added successfully.")
    return staff
