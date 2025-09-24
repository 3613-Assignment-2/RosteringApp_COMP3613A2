from App.database import db

class Shift(db.Model):
    __tablename__ = "shifts"

    shift_id = db.Column(db.Integer, primary_key=True)
    staff_id = db.Column(db.Integer, db.ForeignKey("staff.user_id"), nullable=False)
    date = db.Column(db.Date, nullable=False)
    start_time = db.Column(db.Time, nullable=False)
    end_time = db.Column(db.Time, nullable=False)

    staff = db.relationship("Staff", backref=db.backref("shifts", lazy=True))
    time_entries = db.relationship("TimeEntry", backref="shift", lazy=True)

    def __repr__(self):
        return f"<Shift Staff={self.staff_id} {self.date} {self.start_time}-{self.end_time}>"
    
    def get_json(self):
        return {
            'shiftId': self.shift_id,
            'staffId': self.staff_id,
            'date': self.date,
            'startTime': self.start_time,
            'endTime': self.end_time
        }       
    
    def __init__(self, staff_id, date, start_time, end_time):
        self.staff_id = staff_id
        self.date = date
        self.start_time = start_time
        self.end_time = end_time
    
    def update(self, date=None, start_time=None, end_time=None):
        if date:
            self.date = date
        if start_time:
            self.start_time = start_time
        if end_time:
            self.end_time = end_time
