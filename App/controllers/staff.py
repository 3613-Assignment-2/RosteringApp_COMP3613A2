from App.models import staff
from App.database import db

def create_staff(username, password, role):
    newstaff = staff(username=username, password=password, role=role)
    db.session.add(newstaff)
    db.session.commit()
    return newstaff

def get_staff_by_username(username):
    result = db.session.execute(db.select(staff).filter_by(username=username))
    return result.scalar_one_or_none()

def get_staff(id):
    return db.session.get(staff, id)

def get_all_staff():
    return db.session.scalars(db.select(staff)).all()

def get_all_staff_json():
    all_staff = get_all_staff()
    if not all_staff:
        return []
    all_staff = [staff.get_json() for staff in all_staff]
    return all_staff

def update_staff(id, username):
    staff = get_staff(id)
    if staff:
        staff.username = username
        # user is already in the session; no need to re-add
        db.session.commit()
        return True
    return None
