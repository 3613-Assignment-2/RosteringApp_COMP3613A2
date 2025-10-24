from App.models import shift
from App.database import db

def create_shift(staff_id, date, start_time, end_time):
    newshift = shift(staff_id=staff_id, date=date, start_time=start_time, end_time=end_time)
    db.session.add(newshift)
    db.session.commit()
    return newshift

def get_shift(shift_id):
    return db.session.get(shift, shift_id)

def get_all_shifts():
    return db.session.scalars(db.select(shift)).all()

def get_all_shifts_json():
    shifts = get_all_shifts()
    if not shifts:
        return []
    shifts = [shift.get_json() for shift in shifts]
    return shifts

