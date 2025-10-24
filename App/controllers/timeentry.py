from App.models import timeentry
from App.database import db

def create_timeentry(shift_id, time_in=None, time_out=None):
    newtimeentry = timeentry(shift_id=shift_id, time_in=time_in, time_out=time_out)
    db.session.add(newtimeentry)
    db.session.commit()
    return newtimeentry

def get_timeentry(shift_id):
    return db.session.get(timeentry, shift_id)

def set_time_in(shift_id, time_in):
    get_timeentry(shift_id).set_time_in(time_in)

def set_time_out(shift_id, time_out):
    get_timeentry(shift_id).set_time_in(time_out)
    
def get_all_timeentries():
    return db.session.scalars(db.select(timeentry)).all()

def get_all_timeentries_json():
    timeentries = get_all_timeentries()
    if not timeentries:
        return []
    timeentries = [timeentry.get_json() for timeentry in timeentries]
    return timeentries

